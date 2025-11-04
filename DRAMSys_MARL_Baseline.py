import os
import sys
import subprocess
import time
import re
import json
import random
import json
import numpy as np
import logging

class DRAMSys_MultiAgent():
    def __init__(self):
        self.name = "DRAMSys"
        self.path=os.path.join("../DRAMSys/build/bin/")								# Path to directory holding DRAMSys Executable
        self.config = os.path.join("../DRAMSys/configs/ddr4-example.json")			# Path to ddr4 configuration file

    def extract(self,outstream):
        list = []
        keywords = ["Total Energy", "Average Power", "Total Time", "AVG BW\\IDLE", "BandWidth Possible",
                     "BankGroup Switches", "Bank Switches", "Row Hits", "Row Misses" ]
        energy = re.findall(keywords[0],outstream)
        all_lines = outstream.splitlines()
        for each_idx in range(len(all_lines)):
            if keywords[0] in all_lines[each_idx]:
                list.append(float(all_lines[each_idx].split(":")[1].split()[0])/1e9)
            if keywords[1] in all_lines[each_idx]:
                list.append(float(all_lines[each_idx].split(":")[1].split()[0])/1e3)
            if keywords[2] in all_lines[each_idx]:
                list.append(float(all_lines[each_idx].split(":")[1].split()[0])/1e6)
            if keywords[3] in all_lines[each_idx]:
                list.append(float(all_lines[each_idx].split(":")[1].split()[0]))
            if keywords[4] in all_lines[each_idx]:
                list.append(float(all_lines[each_idx].split(":")[1].split()[0]))
            if keywords[5] in all_lines[each_idx]:
                list.append(float(all_lines[each_idx].split(":")[1].split()[0]))
            if keywords[6] in all_lines[each_idx]:
                list.append(float(all_lines[each_idx].split(":")[1].split()[0]))
            if keywords[7] in all_lines[each_idx]:
                list.append(float(all_lines[each_idx].split(":")[1].split()[0]))
            if keywords[8] in all_lines[each_idx]:
                list.append(float(all_lines[each_idx].split(":")[1].split()[0]))
        list = np.asarray(list)
        if(len(list)==0):
            print(outstream)
        return list

    def runDRAMSys(self):
        path = self.path
        name = self.name
        config = self.config
        final = os.path.join(path,name)
        process = subprocess.Popen([final, config],stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = process.communicate()
        outstream = out.decode()
        list = self.extract(outstream)
        list = list.reshape(9,)
        return list

    def reward_comp(self, energy, latency, bankgrp_switch, bank_switch, row_hits, row_misses, max_bw, avg_bw):
        reward=[0]*10
        target_energy,target_lat,target_bankgrp,target_bank,target_hit,target_miss = 1,0.1,30001,-1,30001,-1		# Ideal Targets
        latency_reward = target_lat/abs((latency-target_lat))
        energy_reward = target_energy/abs((energy-target_energy))
        bw_reward = max_bw/abs((avg_bw-(max_bw+1)))
        bnkgrp_reward = 1/abs((bankgrp_switch-target_bankgrp))
        bnk_reward = 1/abs((bank_switch-target_bank))
        hit_reward = 1/abs((row_hits-target_hit))
        miss_reward = 1/abs((row_misses-target_miss))

        reward[0],reward[1],reward[2],reward[3] = latency_reward,energy_reward,bw_reward,bnkgrp_reward
        reward[4],reward[5],reward[6] = bnk_reward,hit_reward,miss_reward
        tot_reward = sum(reward)
        return reward, tot_reward

if __name__ == "__main__":
    folder_name = f'./Hyperparameter_Tuning/roms/'
    os.makedirs(folder_name, exist_ok=True)
    log_filename = os.path.join(folder_name, f'Base.log')
    logging.basicConfig(filename=log_filename, level=logging.INFO, force=True)
    env = DRAMSys_MultiAgent()
    cumulative_reward = 0
    timesteps = 17563																							# Total Timesteps
    lat,en,bankgrp,bank,hit,miss,bw,avgbw,r=[],[],[],[],[],[],[],[],[]
    for i in range(0,timesteps):
        print("Timestep:",i+1)
        logging.info(f"Step {i+1}:")
        obs = env.runDRAMSys()
        reward, tot_reward = env.reward_comp(obs[0],obs[2],obs[3],obs[4],obs[5],obs[6],obs[7],obs[8])
        en.append(obs[0])
        lat.append(obs[2])
        bankgrp.append(obs[3])
        bank.append(obs[4])
        hit.append(obs[5])
        miss.append(obs[6])
        avgbw.append(obs[7])
        bw.append(obs[8])
        r.append(tot_reward)
        logging.info(f"Observation {obs}")
        logging.info(f"Reward: {tot_reward}")
        if (i >= 14000):																						# Warmup Timesteps
           cumulative_reward+=tot_reward
	# Save Metrics
    with open('./Hyperparameter_Tuning/Base-Merics.txt', 'w') as f:
        f.write(f"Cumulative Reward: {cumulative_reward}\n")
        f.write(f"{en}\n\n")
        f.write(f"{lat}\n\n")
        f.write(f"{bankgrp}\n\n")
        f.write(f"{bank}\n\n")
        f.write(f"{hit}\n\n")
        f.write(f"{miss}\n\n")
        f.write(f"{avgbw}\n\n")
        f.write(f"{bw}\n\n")
        f.write(f"{r}\n\n")
