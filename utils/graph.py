import numpy as np
import pandas as pd
from scipy import stats
from collections import defaultdict 
from functools import cmp_to_key
from scipy.optimize import nnls
 
    
class Graph: 
    def __init__(self,vertices): 
        self.V= vertices            
        self.graph = defaultdict(list)  
 
    def addEdge(self,u,v): 
        self.graph[u].append(v) 
   
    def printPathsFunc(self, u, d, visited, path, current_path_list): 
        visited[u]= True
        path.append(u) 

        if u == d: 
            path_copy = path[:]
            current_path_list.append(path_copy)
        else: 
            for i in self.graph[u]: 
                if visited[i]==False: 
                    self.printPathsFunc(i, d, visited, path, current_path_list) 
                      
        path.pop() 
        visited[u]= False
        return current_path_list

        
    def printPaths(self, s, d): 
        total_results = []
        for start in s:
            for dest in d:
                path = []
                visited =[False]*(self.V) 
                current_path_list = []
                current_path_results = self.printPathsFunc(start, dest, visited, path, current_path_list) 
                if len(current_path_results) != 0:
                    total_results.extend(current_path_results)
        return total_results
    
    
def graph_process(config_path):
    cluster_unify = []
    partial_order = []
    start_candidates = []
    end_candidates = []
    
    f = open(config_path, 'r')
    while True:
        line = f.readline()
        if '=' in line:
            unify = list(map(int, line.split('=')))
            cluster_unify.append(unify)
        elif '<' in line:
            order = list(map(int, line.split('<')))
            partial_order.append(order)
            start_candidates.append(order[0])
            end_candidates.append(order[1])
            
        if not line: break
    f.close()
        
    start = []
    end = []
    for element in start_candidates:
        if element in end_candidates:
            continue
        start.append(element)
    
    for element in end_candidates:
        if element in start_candidates:
            continue
        end.append(element)
    
    start = list(set(start))
    end = list(set(end))
    return start, end, partial_order, cluster_unify



def generate_graph(partial_order_list, vertex_num):
    cluster_graph = Graph(vertex_num)
    for pair in partial_order_list:
        cluster_graph.addEdge(pair[0], pair[1])
    return cluster_graph 


def save_graph_config(ordered_list, name):
    f = open("./graph_config/{}".format(name), 'w')
        
    for i in range(len(ordered_list) - 1):
        f.write('{}<{}\n'.format(ordered_list[i+1][0], ordered_list[i][0]))
    
    for orders in ordered_list:
        if len(orders) >= 2:
            f.write(str(orders[0]))
            for element in orders[1:]:
                f.write('={}'.format(element))
            f.write('\n')        
    f.close()        
    
    
    
def graph_inference_census(df, hist, cluster_num, file_path, col_name = 'TOTPOP_CY'):
    def numeric_compare(x, y):
        pop_list1 = result_list[x]
        pop_list2 = result_list[y]
        tTestResult = stats.ttest_ind(pop_list1, pop_list2)
        if (tTestResult.pvalue < 0.05) and (np.mean(pop_list1) < np.mean(pop_list2)):
            return 1
        elif (tTestResult.pvalue < 0.05) and (np.mean(pop_list1) >= np.mean(pop_list2)):
            return -1
        else:
            return 0

    result_list = []
    
    for i in range(cluster_num - 1):
        result_list.append([])

    for _ in range(100):
        msk = np.random.rand(len(df)) < 0.5
        df_train = df[msk][["Directory", col_name]]
        df_test = df[~msk][["Directory", col_name]]
        selected_hist_train = hist.loc[df_train['Directory'] - 1]
        selected_hist_test = hist.loc[df_test['Directory'] - 1]

        train_X = selected_hist_train.values
        train_y = df_train["TOTPOP_CY"].values
        test_X = selected_hist_test.values
        test_y = df_test["TOTPOP_CY"].values
        result = nnls(train_X, train_y, 100)[0]
        for i in range(len(result)):
            result_list[i].append(result[i])

    sorted_list = sorted(range(cluster_num - 1), key=cmp_to_key(numeric_compare))
    ordered_list = []
    ordered_list.append([sorted_list[0]])
    curr = 0
    for i in range(len(sorted_list) - 1):
        if numeric_compare(sorted_list[i], sorted_list[i+1]) == 0:
            ordered_list[curr].append(sorted_list[i+1])
        else:
            curr += 1
            ordered_list.append([sorted_list[i+1]])

    ordered_list.append([cluster_num - 1])
    save_graph_config(ordered_list, file_path)
    return './graph_config/{}'.format(file_path)
            
    
            
def graph_inference_nightlight(grid_df, nightlight_df, cluster_num, file_path):
    def numeric_compare(x, y):
        pop_list1 = df_merge_group.get_group(x)['light_sum'].tolist()
        pop_list2 = df_merge_group.get_group(y)['light_sum'].tolist()
        tTestResult = stats.ttest_ind(pop_list1, pop_list2)
        if (tTestResult.pvalue < 0.01) and (np.mean(pop_list1) < np.mean(pop_list2)):
            return 1
        elif (tTestResult.pvalue < 0.01) and (np.mean(pop_list1) >= np.mean(pop_list2)):
            return -1
        else:
            return 0
        
    df_merge = pd.merge(nightlight_df, grid_df, how='left', on='y_x')
    df_merge = df_merge.dropna()
    df_merge_group = df_merge.groupby('cluster_id')
    
    sorted_list = sorted(range(cluster_num - 1), key=cmp_to_key(numeric_compare))
    ordered_list = []
    ordered_list.append([sorted_list[0]])
    curr = 0
    for i in range(len(sorted_list) - 1):
        if numeric_compare(sorted_list[i], sorted_list[i+1]) == 0:
            ordered_list[curr].append(sorted_list[i+1])
        else:
            curr += 1
            ordered_list.append([sorted_list[i+1]])
            
    ordered_list.append([cluster_num - 1])        
    save_graph_config(ordered_list, file_path)
    return './graph_config/{}'.format(file_path)

    
    