import os
import sys
import subprocess
import time
import re
import json
import yaml
import random
import numpy as np
import logging
class DRAMSys_MultiAgent():
    def __init__(self,seed = 9):
        self.seed = seed
        self.old_epsilon = 0.8
        self.new_epsilon = 0.001
        self.threshold = 14000													# Warmup Timesteps
        self.discount = 0.9
        self.learning_rate = 0.1

        self.sch_table = np.zeros((3,3,7))
        self.buf_table = np.zeros((3,3,7))
        self.arb_table = np.zeros((3,3,7))
        self.page_table = np.zeros((4,4,7))
        self.resp_table = np.zeros((2,2,3))
        self.ref_table = np.zeros((2,2,3))
        self.req_buf_table = np.zeros((8,8,3))
        self.ref_max_post_table = np.zeros((4,4,3))
        self.ref_max_pull_table = np.zeros((4,4,3))
        self.max_act_table = np.zeros((8,8,7))

        self.tables = [self.sch_table, self.buf_table, self.arb_table, self.page_table, self.resp_table, self.ref_table,
                       self.req_buf_table, self.ref_max_post_table, self.ref_max_pull_table, self.max_act_table]
        np.random.seed(self.seed)
        self.q_table_rngs = [np.random.RandomState(self.seed + i) for i in range(len(self.tables))]
        self.name = "DRAMSys"
        self.path=os.path.join("../DRAMSys/build/bin/")							# Path to directory holding DRAMSys Executable
        self.config = os.path.join("../DRAMSys/configs/ddr4-example.json")		# Path to ddr4 configuration file


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
    
    def action_decoder(self, action):
        decoded = {}
        scheduler = {0:"Fifo", 1:"FrFcfsGrp", 2:"FrFcfs"}
        schedulerbuffer = {0:"Bankwise", 1:"ReadWrite", 2:"Shared"}
        arbiter = {0:"Simple", 1:"Fifo", 2:"Reorder"}
        page_policy = {0:"Open", 1:"OpenAdaptive", 2:"Closed", 3:"ClosedAdaptive"}
        respqueue = {0:"Fifo", 1:"Reorder"}
        refreshpolicy = {0:"NoRefresh", 1:"AllBank"}
        request_buffer_size = {0:1, 1:2, 2:4, 3:8, 4:16, 5:32, 6:64, 7:128}
        refreshmaxpostponed = {0:1, 1:2, 2:4, 3:8}
        refreshmaxpulledin = {0:1, 1:2, 2:4, 3:8}
        max_active_transactions = {0:1, 1:2, 2:4, 3:8, 4:16, 5:32, 6:64, 7:128}

        decoded["Scheduler"]  =  scheduler[action[0]]
        decoded["SchedulerBuffer"]  =  schedulerbuffer[action[1]]
        decoded["Arbiter"] =  arbiter[action[2]]
        decoded["PagePolicy"] = page_policy[action[3]]
        decoded["RespQueue"] = respqueue[action[4]]
        decoded["RefreshPolicy"] = refreshpolicy[action[5]]
        decoded["RequestBufferSize"] = request_buffer_size[action[6]]
        decoded["RefreshMaxPostponed"] = refreshmaxpostponed[action[7]]
        decoded["RefreshMaxPulledin"] = refreshmaxpulledin[action[8]]
        decoded["MaxActiveTransactions"] = max_active_transactions[action[9]]
        return decoded

    def modify_dramsys(self, action):
        success = False
        mc_config = "../DRAMSys/configs/mcconfig/fr_fcfs_test.json"						# Path to Memory controller parameters' configuration file
        try:
            with open (mc_config, "r") as JsonFile:
                data = json.load(JsonFile)
                data['mcconfig']['Scheduler'] = action['Scheduler']
                data['mcconfig']['SchedulerBuffer'] = action['SchedulerBuffer']
                data['mcconfig']['Arbiter'] = action['Arbiter']
                data['mcconfig']['PagePolicy'] = action['PagePolicy']
                data['mcconfig']['RespQueue'] = action['RespQueue']
                data['mcconfig']['RefreshPolicy'] = action['RefreshPolicy']
                data['mcconfig']['RequestBufferSize'] = action['RequestBufferSize']
                data['mcconfig']['RefreshMaxPostponed'] = action['RefreshMaxPostponed']
                data['mcconfig']['RefreshMaxPulledin'] = action['RefreshMaxPulledin']
                data['mcconfig']['MaxActiveTransactions'] = action['MaxActiveTransactions']
                with open (mc_config, "w") as JsonFile:
                    json.dump(data,JsonFile)
                success = True
        except Exception as e:
            print(str(e))
            success = False
        return success

    def choose_action(self, index, q_table, state, iteration):
            num_actions = q_table.shape[1]
            epsilon = self.old_epsilon
            if (iteration >= self.threshold):
                epsilon = self.new_epsilon
            rng = self.q_table_rngs[index]

            if rng.uniform(0, 1) < epsilon:
                action = rng.randint(0, num_actions)
            else:
                action = np.argmax(np.sum(q_table[state, :, :], axis=1))
            return action
    
    def reward_comp(self, energy, latency, bankgrp_switch, bank_switch, row_hits, row_misses, max_bw, avg_bw):
        reward=[0]*7
        target_energy,target_lat,target_bankgrp,target_bank,target_hit,target_miss = 1,0.1,30001,-1,30001,-1 			# Ideal Targets
        latency_reward = target_lat/abs((latency-target_lat))
        energy_reward = target_energy/abs((energy-target_energy))
        bw_reward = max_bw/abs((avg_bw-(max_bw+1)))
        bnkgrp_reward = 1/abs((bankgrp_switch-target_bankgrp))
        bnk_reward = 1/abs((bank_switch-target_bank))
        hit_reward = 1/abs((row_hits-target_hit))
        miss_reward = 1/abs((row_misses-target_miss))
        # Reward Array
        reward[0],reward[1],reward[2],reward[3] = latency_reward, energy_reward, bw_reward, bnkgrp_reward
        reward[4],reward[5],reward[6] = bnk_reward, hit_reward, miss_reward
        return reward, sum(reward)

    def step(self, q_table, state1, state2, action1, action2, reward, reward_cons):
        for i in reward_cons:
            Qsa1 = q_table[state1][action1][i]
            Qsa2 = q_table[state2][action2][i]
            Qsa1 = Qsa1 + (self.learning_rate * (reward[i] + self.discount * Qsa2 - Qsa1))
            q_table[state1][action1][i] = Qsa1

    def multiagent_step(self, states, actions, reward):
        # Scheduler, Scheduler Buffer, Arbiter, Page Policy
        for i in range(0, 4):
            self.step(self.tables[i], states[0][i], states[1][i], actions[0][i], actions[1][i], reward, [0, 1, 2, 3, 4, 5, 6])
        # Response_Queue, Refresh Policy, Request Buffer Size, Refresh Max Postponed, Refresh Max Pulledin
        for i in range(4, 9):
            self.step(self.tables[i], states[0][i], states[1][i], actions[0][i], actions[1][i], reward, [0, 1, 2])
        # Max Active Transactions
        self.step(self.max_act_table, states[0][9], states[1][9], actions[0][9], actions[1][9], reward, [0, 1, 2, 3, 4, 5, 6])

if __name__ == "__main__":
    learning_rates = [0.1]
    discount_factors = [0.9]
    timesteps = 17563																								# Total Timesteps
    for lr in learning_rates:
        for df in discount_factors:
            folder_name = f'./Hyperparameter_Tuning/roms/'
            os.makedirs(folder_name, exist_ok=True)
            log_filename = os.path.join(folder_name, f'Train.log')
            logging.basicConfig(filename=log_filename, level=logging.INFO, force=True)
            env = DRAMSys_MultiAgent()
            env.discount = df
            env.learning_rate = lr

            cumulative_reward = 0
            state1 = [0] * 10
            action1 = [
                env.choose_action(0, env.sch_table, state1[0], 0),
                env.choose_action(1, env.buf_table, state1[1], 0),
                env.choose_action(2, env.arb_table, state1[2], 0),
                env.choose_action(3, env.page_table, state1[3], 0),
                env.choose_action(4, env.resp_table, state1[4], 0),
                env.choose_action(5, env.ref_table, state1[5], 0),
                env.choose_action(6, env.req_buf_table, state1[6], 0),
                env.choose_action(7, env.ref_max_post_table, state1[7], 0),
                env.choose_action(8, env.ref_max_pull_table, state1[8], 0),
                env.choose_action(9, env.max_act_table, state1[9], 0)
            ]

            lat, en, bankgrp, bank, hit, miss, bw, avgbw, r = [], [], [], [], [], [], [], [], []

            for i in range(timesteps):
                logging.info(f"Step {i+1}:")
                print(f"[LR={lr} | DF={df}] → Timestep {i+1}")
                action_decoded = env.action_decoder(action1)
                logging.info(f"States: {state1}, Action: {action_decoded}")
                write = env.modify_dramsys(action_decoded)
                if write:
                    obs = env.runDRAMSys()
                    reward, tot_reward = env.reward_comp(obs[0], obs[2], obs[3], obs[4], obs[5], obs[6], obs[7], obs[8])
                    en.append(obs[0])
                    lat.append(obs[2])
                    bankgrp.append(obs[3])
                    bank.append(obs[4])
                    hit.append(obs[5])
                    miss.append(obs[6])
                    avgbw.append(obs[7])
                    bw.append(obs[8])
                    r.append(tot_reward)

                    if i >= env.threshold:
                        cumulative_reward += tot_reward

                    logging.info(f"Observation: {obs}")
                    logging.info(f"Reward: {tot_reward}")

                    state2 = action1
                    action2 = [
                        env.choose_action(0, env.sch_table, state2[0], i),
                        env.choose_action(1, env.buf_table, state2[1], i),
                        env.choose_action(2, env.arb_table, state2[2], i),
                        env.choose_action(3, env.page_table, state2[3], i),
                        env.choose_action(4, env.resp_table, state2[4], i),
                        env.choose_action(5, env.ref_table, state2[5], i),
                        env.choose_action(6, env.req_buf_table, state2[6], i),
                        env.choose_action(7, env.ref_max_post_table, state2[7], i),
                        env.choose_action(8, env.ref_max_pull_table, state2[8], i),
                        env.choose_action(9, env.max_act_table, state2[9], i)
                    ]
                    env.multiagent_step([state1, state2], [action1, action2], reward)
                    state1, action1 = state2, action2

            # Save result tables and cumulative reward
            result_file_path = os.path.join(folder_name, f'Results.txt')
            with open(result_file_path, 'a') as result_file:
                table_names = [
                    "Scheduler", "Buffer", "Arbiter", "Page", "Response", "Refresh",
                    "Request Buffer", "Ref Max Post", "Ref Max Pull", "Max Activate"
                ]
                for table, name in zip(env.tables, table_names):
                    result_file.write(f"{name} Table:\n{table}\n\n")
                result_file.write(f"Cumulative Reward: {cumulative_reward}\n")

            # Save metrics
            metrics_file_path = os.path.join(folder_name, f'Metrics.txt')
            with open(metrics_file_path, 'a') as f:
                for metric in [en, lat, bankgrp, bank, hit, miss, bw, avgbw, r]:
                    f.write(f"{metric}\n\n")

            line_file_path = './line.txt'
            with open(line_file_path, 'w') as line_file:
                line_file.write('0')
