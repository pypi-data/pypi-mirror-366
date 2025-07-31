import torch
import torch.nn as nn
import time
import numpy as np
import threading
import queue
import copy
import os

from .input import Base
from .util import load_vap_model
from .models.vap import VapGPT
from .models.vap_bc_2type import VapGPT_bc_2type
from .models.vap_nod import VapGPT_nod
from .models.config import VapConfig
# from .models.vap_prompt import VapGPT_prompt

class Maai():
    
    BINS_P_NOW = [0, 1]
    BINS_PFUTURE = [2, 3]
    
    CALC_PROCESS_TIME_INTERVAL = 100

    def __init__(self, mode, frame_rate, context_len_sec, language: str = "jp", audio_ch1: Base = None, audio_ch2: Base = None, num_channels: int = 2, cpc_model: str = os.path.expanduser("~/.cache/cpc/60k_epoch4-d0f474de.pt"), device: str = "cpu", cache_dir: str = None, force_download: bool = False):

        conf = VapConfig()
        
        if mode in ["vap", "vap_mc"]:
            self.vap = VapGPT(conf)
        
        elif mode == "bc_2type":
            self.vap = VapGPT_bc_2type(conf)
        
        elif mode == "nod":
            self.vap = VapGPT_nod(conf)
        
        elif mode == "vap_prompt":
            from .models.vap_prompt import VapGPT_prompt
            self.vap = VapGPT_prompt(conf)
        
        self.device = device

        if self.device not in ["cpu", "cuda"]:
            raise ValueError("Device must be 'cpu' or 'cuda'.")

        sd = load_vap_model(mode, frame_rate, context_len_sec, language, device, cache_dir, force_download)
        self.vap.load_encoder(cpc_model=cpc_model)
        self.vap.load_state_dict(sd, strict=False)

        # The downsampling parameters are not loaded by "load_state_dict"
        self.vap.encoder1.downsample[1].weight = nn.Parameter(sd['encoder.downsample.1.weight'])
        self.vap.encoder1.downsample[1].bias = nn.Parameter(sd['encoder.downsample.1.bias'])
        self.vap.encoder1.downsample[2].ln.weight = nn.Parameter(sd['encoder.downsample.2.ln.weight'])
        self.vap.encoder1.downsample[2].ln.bias = nn.Parameter(sd['encoder.downsample.2.ln.bias'])
        
        self.vap.encoder2.downsample[1].weight = nn.Parameter(sd['encoder.downsample.1.weight'])
        self.vap.encoder2.downsample[1].bias = nn.Parameter(sd['encoder.downsample.1.bias'])
        self.vap.encoder2.downsample[2].ln.weight = nn.Parameter(sd['encoder.downsample.2.ln.weight'])
        self.vap.encoder2.downsample[2].ln.bias = nn.Parameter(sd['encoder.downsample.2.ln.bias'])

        self.vap.to(self.device)
        self.vap = self.vap.eval()
        
        self.mode = mode
        self.mic1 = audio_ch1
        self.mic2 = audio_ch2

        # Always subscribe a dedicated queue for each mic if possible
        self._mic1_queue = self.mic1.subscribe()
        self._mic2_queue = self.mic2.subscribe()

        self.audio_contenxt_lim_sec = context_len_sec
        self.frame_rate = frame_rate
        
        # Context length of the audio embeddings (depends on frame rate)
        self.audio_context_len = int(self.audio_contenxt_lim_sec * self.frame_rate)
        
        self.sampling_rate = 16000
        self.frame_contxt_padding = 320 # Independe from frame size
        
        # Frame size
        # 10Hz -> 320 + 1600 samples
        # 20Hz -> 320 + 800 samples
        # 50Hz -> 320 + 320 samples
        self.audio_frame_size = self.sampling_rate // self.frame_rate + self.frame_contxt_padding
        
        self.current_x1_audio = []
        self.current_x2_audio = []
        
        self.result_p_now = 0.
        self.result_p_future = 0.
        self.result_p_bc_react = 0.
        self.result_p_bc_emo = 0.
        self.result_p_bc = 0.
        self.result_p_nod_short = 0.
        self.result_p_nod_long = 0.
        self.result_p_nod_long_p = 0.
        self.result_last_time = -1
        
        self.result_vad = [0., 0.]

        self.process_time_abs = -1

        self.e1_context = []
        self.e2_context = []
        
        self.list_process_time_context = []
        self.last_interval_time = time.time()
        
        self.result_dict_queue = queue.Queue()
    
    def worker(self):
        while True:
            x1 = self.mic1.get_audio_data(self._mic1_queue)
            x2 = self.mic2.get_audio_data(self._mic2_queue)
            self.process(x1, x2)

    def start_process(self):
        self.mic1.start_process()
        self.mic2.start_process()
        threading.Thread(target=self.worker, daemon=True).start()  
    
    def process(self, x1, x2):
        
        time_start = time.time()

        # Initialize buffer if empty
        if len(self.current_x1_audio) == 0:
            self.current_x1_audio = np.zeros(self.frame_contxt_padding)
        if len(self.current_x2_audio) == 0:
            self.current_x2_audio = np.zeros(self.frame_contxt_padding)
        # Add to buffer
        self.current_x1_audio = np.concatenate([self.current_x1_audio, x1])
        self.current_x2_audio = np.concatenate([self.current_x2_audio, x2])

        # Return if the buffer does not have enough length
        if len(self.current_x1_audio) < self.audio_frame_size:
            return

        # Extract data for inference
        x1_proc = self.current_x1_audio.copy()
        x2_proc = self.current_x2_audio.copy()

        x1_dist = x1_proc[self.frame_contxt_padding:]
        x2_dist = x2_proc[self.frame_contxt_padding:]

        with torch.no_grad():
            
            # Convert to tensors efficiently
            x1_ = torch.from_numpy(x1_proc).float().view(1, 1, -1).to(self.device)
            x2_ = torch.from_numpy(x2_proc).float().view(1, 1, -1).to(self.device)

            e1, e2 = self.vap.encode_audio(x1_, x2_)
            
            self.e1_context.append(e1)
            self.e2_context.append(e2)
            
            if len(self.e1_context) > self.audio_context_len:
                self.e1_context = self.e1_context[-self.audio_context_len:]
            if len(self.e2_context) > self.audio_context_len:
                self.e2_context = self.e2_context[-self.audio_context_len:]
            
            x1_context_ = torch.cat(self.e1_context, dim=1).to(self.device)
            x2_context_ = torch.cat(self.e2_context, dim=1).to(self.device)

            # o1 = self.vap.ar_channel(x1_context_, attention=False)  # ["x"]
            # o2 = self.vap.ar_channel(x2_context_, attention=False)  # ["x"]
            # out = self.vap.ar(o1["x"], o2["x"], attention=False)

            # Outputs
            if self.mode in ["vap", "vap_mc", "vap_prompt"]:

                out = self.vap.forward(x1_context_, x2_context_)
                
                self.result_dict_queue.put({
                    "t": time.time(),
                    "x1": copy.copy(x1_dist), "x2": copy.copy(x2_dist),
                    "p_now": copy.copy(out['p_now']), "p_future": copy.copy(out['p_future']),
                    "vad": copy.copy(out['vad'])
                })
                
            elif self.mode == "bc_2type":
                
                out = self.vap.forward(x1_context_, x2_context_)
                
                self.result_dict_queue.put({
                    "t": time.time(),
                    "x1": copy.copy(x1_dist), "x2": copy.copy(x2_dist),
                    "p_bc_react": copy.copy(out['p_bc_react']),
                    "p_bc_emo": copy.copy(out['p_bc_emo'])
                })
            
            elif self.mode == "nod":
                
                out = self.vap.forward(x1_context_, x2_context_)

                self.result_dict_queue.put({
                    "t": time.time(),
                    "x1": copy.copy(x1_dist), "x2": copy.copy(x2_dist),
                    "p_bc": copy.copy(out['p_bc']),
                    "p_nod_short": copy.copy(out['p_nod_short']),
                    "p_nod_long": copy.copy(out['p_nod_long']),
                    "p_nod_long_p": copy.copy(out['p_nod_long_p'])
                })
                
            # self.result_last_time = time.time()
            
            time_process = time.time() - time_start
            
            # Calculate the average encoding time
            self.list_process_time_context.append(time_process)
            
            if len(self.list_process_time_context) > self.CALC_PROCESS_TIME_INTERVAL:
                ave_proc_time = np.average(self.list_process_time_context)
                num_process_frame = len(self.list_process_time_context) / (time.time() - self.last_interval_time)
                self.last_interval_time = time.time()

                print(f'[{self.mode}] Average processing time: {ave_proc_time:.5f} [sec], #process/sec: {num_process_frame:.3f}')
                self.list_process_time_context = []
            
            self.process_time_abs = time.time()

        # Keep only the last samples in the buffer
        self.current_x1_audio = self.current_x1_audio[-self.frame_contxt_padding:]
        self.current_x2_audio = self.current_x2_audio[-self.frame_contxt_padding:]
    
    def get_result(self):
        return self.result_dict_queue.get()
    
    def set_prompt_ch1(self, prompt: str):
        """
        Set the prompt text for speaker 1. This method is only available for the 'vap_prompt' mode.
        
        Args:
            prompt (str): The prompt text for speaker 1.
        """
        
        if self.mode != "vap_prompt":
            raise ValueError("This method is only available for the 'vap_prompt' mode.")
        
        self.vap.set_prompt_ch1(prompt)
    
    def set_prompt_ch2(self, prompt: str):
        """
        Set the prompt text for speaker 2. This method is only available for the 'vap_prompt' mode.
        
        Args:
            prompt (str): The prompt text for speaker 2.
        """
        
        if self.mode != "vap_prompt":
            raise ValueError("This method is only available for the 'vap_prompt' mode.")
        
        self.vap.set_prompt_ch2(prompt)
    