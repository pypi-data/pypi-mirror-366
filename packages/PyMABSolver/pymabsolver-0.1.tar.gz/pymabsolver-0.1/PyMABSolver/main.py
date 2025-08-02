#############################################################################
# Owner: Shreyas Sawant
# Function: MAB Python library with 4 different methods of solving MAB.
#############################################################################

import random
import matplotlib.pyplot as plt


class MABSolver:
    def __init__(self, n, t, tf = None, eps = None):
        self.n = n
        self.t = t
        self.tf = tf
        self.epsilon = eps

        numlist = []
        self.win_prob_list = []
        for _ in range(self.n):
            numlist.append(random.randint(0, 100))
            self.win_prob_list.append(round(random.uniform(0 ,1), 2))

        self.selection_prob_list = self.get_selection_probs(total=sum(numlist), numlist=numlist)

    def get_selection_probs(self, total, numlist):
        prob_list = []
        for i in range(len(numlist)):
            prob_list.append(round(numlist[i] / total, 2))
        
        return prob_list
    
    def exploration(self):
        # Exploration implementation.
        cdf = []
        prob_sum = 0
        for i in range(len(self.selection_prob_list)):
            prob_sum += self.selection_prob_list[i]
            cdf.append(round(prob_sum, 2))

        rand_probs1 = []
        rand_probs2 = []
        for n in range(self.t):
            rand_probs1.append(round(random.uniform(0 ,1), 2))
            rand_probs2.append(round(random.uniform(0 ,1), 2))

        selected_arms = []
        for i in rand_probs1:
            for j in cdf:
                if i < j:
                    idx = cdf.index(j)
                    break
            
            selected_arms.append(idx)

        rewards = []
        for i in range(len(rand_probs2)):
            if rand_probs2[i] <= self.win_prob_list[selected_arms[i]]:
                rewards.append(1)
            
            else:
                rewards.append(0)

        print("Total reward:", sum(rewards))
        max_reward_possible = max(self.win_prob_list) * self.t
        print("Maximum possible reward:", max_reward_possible)

        avg_rew_list = []
        total_rew = 0
        ctr = 0

        for i in rewards:
            total_rew += i
            ctr += 1
            avg_rew_list.append(total_rew/ctr)
        
        return avg_rew_list, rewards
    
    def exploitation(self):
        # Exploration implementation.
        cdf = []
        prob_sum = 0
        for i in range(len(self.selection_prob_list)):
            prob_sum += self.selection_prob_list[i]
            cdf.append(round(prob_sum, 2))

        rand_prob = round(random.uniform(0 ,1), 2)
        rand_probs2 = []
        for _ in range(self.t):
            rand_probs2.append(round(random.uniform(0 ,1), 2))

        selected_arms = []
        for i in cdf:
            if rand_prob < i:
                idx = cdf.index(i)
                break

        for i in range(self.t):
            selected_arms.append(idx)

        rewards = []
        for i in range(len(rand_probs2)):
            if rand_probs2[i] <= self.win_prob_list[selected_arms[i]]:
                rewards.append(1)
            
            else:
                rewards.append(0)

        print("Total reward:", sum(rewards))
        max_reward_possible = max(self.win_prob_list) * self.t
        print("Maximum possible reward:", max_reward_possible)

        avg_rew_list = []
        total_rew = 0
        ctr = 0

        for i in rewards:
            total_rew += i
            ctr += 1
            avg_rew_list.append(total_rew/ctr)
        
        return avg_rew_list, rewards
    
    def fixed_exploration_greedy_exploitation(self):
        cdf = []
        prob_sum = 0
        for i in range(len(self.selection_prob_list)):
            prob_sum += self.selection_prob_list[i]
            cdf.append(round(prob_sum, 2))

        rand_probs1 = []
        rand_probs2 = []
        for _ in range(self.tf):
            rand_probs1.append(round(random.uniform(0 ,1), 2))
            rand_probs2.append(round(random.uniform(0 ,1), 2))

        selected_arms = []
        for i in rand_probs1:
            for j in cdf:
                if i < j:
                    idx = cdf.index(j)
                    break
            
            selected_arms.append(idx)

        rewards = []
        win_dict = {}
        count_selection = []
        for i in range(self.n):
            win_dict[i] = 0
            count_selection.append(selected_arms.count(i))

        for i in range(len(rand_probs2)):
            if rand_probs2[i] <= self.win_prob_list[selected_arms[i]]:
                rewards.append(1)
                win_dict[selected_arms[i]] += 1
            
            else:
                rewards.append(0)

        actual_win_prob = []
        for i in range(self.n):
            if count_selection[i] > 0:
                actual_win_prob.append(win_dict[i]/count_selection[i])
            
            else:
                actual_win_prob.append(win_dict[i]/(count_selection[i]+1))

        rand_probs2 = []
        for _ in range(self.t - self.tf):
            rand_probs2.append(round(random.uniform(0 ,1), 2))

        selected_arms = []
        for i in range(self.t):
            selected_arms.append(actual_win_prob.index(max(actual_win_prob)))

        for i in range(len(rand_probs2)):
            if rand_probs2[i] <= self.win_prob_list[selected_arms[i]]:
                rewards.append(1)
            
            else:
                rewards.append(0)

        print("Total reward:", sum(rewards))
        max_reward_possible = max(self.win_prob_list) * self.t
        print("Maximum possible reward:", max_reward_possible)

        avg_rew_list = []
        total_rew = 0
        ctr = 0

        for i in rewards:
            total_rew += i
            ctr += 1
            avg_rew_list.append(total_rew/ctr)
        
        return avg_rew_list, rewards
    
    def epsilon_greedy(self):
        cdf = []
        prob_sum = 0
        for i in range(len(self.selection_prob_list)):
            prob_sum += self.selection_prob_list[i]
            cdf.append(round(prob_sum, 2))

        selected_arms = []
        rewards = []
        win_dict = {}
        expr_ctr = 0
        count_selection = {}
        actual_win_prob = {}
        rand_prob1 = round(random.uniform(0 ,1), 2) # For random exploitation.
        for i in cdf:
            if rand_prob1 < i:
                expl_idx = cdf.index(i)
                break

        for j in range(self.n):
            win_dict[j] = 0
            count_selection[j] = 0
            actual_win_prob[j] = 0

        for _ in range(self.t):
            rand_num = round(random.uniform(0, 1), 2)
            
            if rand_num < self.epsilon:
                rand_prob1 = round(random.uniform(0 ,1), 2)
                rand_prob2 = round(random.uniform(0 ,1), 2)

                for i in cdf:
                    if rand_prob1 < i:
                        idx = cdf.index(i)
                        break
                
                selected_arms.append(idx)

                if rand_prob2 <= self.win_prob_list[selected_arms[-1]]:
                    rewards.append(1)
                    win_dict[selected_arms[-1]] += 1
                
                else:
                    rewards.append(0)

                for i in range(self.n):
                    count_selection[i] = selected_arms.count(i)
                
                for i in range(self.n):
                    if count_selection[i] > 0:
                        actual_win_prob[i] = win_dict[i]/count_selection[i]
                    
                    else:
                        actual_win_prob[i] = win_dict[i]/(count_selection[i]+1)
                
                expr_ctr += 1

            else:
                if expr_ctr == 0:
                    rand_prob2 = round(random.uniform(0 ,1), 2)

                    selected_arms.append(expl_idx)

                    if rand_prob2 <= self.win_prob_list[selected_arms[-1]]:
                        rewards.append(1)
                        win_dict[selected_arms[-1]] += 1
                    
                    else:
                        rewards.append(0)

                else:
                    rand_prob2 = round(random.uniform(0 ,1), 2)
                    selected_arms.append(list(actual_win_prob.values()).index(max(actual_win_prob.values())))
                    if rand_prob2 <= self.win_prob_list[selected_arms[-1]]:
                        rewards.append(1)
                        win_dict[selected_arms[-1]] += 1
                    
                    else:
                        rewards.append(0)

        print("Total reward:", sum(rewards))
        max_reward_possible = max(self.win_prob_list) * self.t
        print("Maximum possible reward:", max_reward_possible)

        avg_rew_list = []
        total_rew = 0
        ctr = 0

        for i in rewards:
            total_rew += i
            ctr += 1
            avg_rew_list.append(total_rew/ctr)

        return avg_rew_list, rewards
    
    def plot_comparison(self, avg_rew_list_expr=None, avg_rew_list_expl=None, avg_rew_list_fege=None, avg_rew_list_eps=None):
        placeholders = []
        if avg_rew_list_expr:
            plt.plot(range(self.t), avg_rew_list_expr)
            placeholders.append('Pure Exploration')
        
        if avg_rew_list_expl:
            plt.plot(range(self.t), avg_rew_list_expl)
            placeholders.append('Pure Exploitation')

        if avg_rew_list_fege:
            plt.plot(range(self.t), avg_rew_list_fege)
            placeholders.append('Fixed Explore + Greedy Exploit')
        
        if avg_rew_list_eps:
            plt.plot(range(self.t), avg_rew_list_eps)
            placeholders.append('Epsilon Greedy')

        plt.legend(placeholders)
        plt.show()