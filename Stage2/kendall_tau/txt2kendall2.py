import sys
from scipy import stats
import numpy as np
import pandas as pd
import itertools

def adj_rank(pog_line):
    pog_line.strip()
    pog_line.replace(" ", "")
    print('pog input', pog_line)
    vertice = pog_line.split('>')
    cl = [i.split('=') for i in vertice]
    count = 1
    ranks = []
    for i in range(len(cl)):
        if len(cl[i]) == 1:
            ranks.append(count)
            count += 1
        else:
            b = len(cl[i])
            tot = b * count + b * (b - 1) / 2
            m = tot / b
            ranks += [m] * b
            count += b
    cluster_rank_flat = [int(j) for i in cl for j in i]
    print('cluster',cluster_rank_flat)
    print('cluster_adj_rank',ranks)
    adj_rank_list = [0] * len(cluster_rank_flat)
    for i in range(len(cluster_rank_flat)):
        adj_rank_list[cluster_rank_flat[i]] = ranks[i]
    return adj_rank_list


if __name__ == '__main__':
    argument = sys.argv
    del argument[0]
    pog_lines = open(argument[0], 'r')
    colnames = open(argument[1], 'r')
    result_dir = '../results/'
    pog_lines = pog_lines.read().split('\n')
    pog_lines = [elem for elem in pog_lines if elem.strip()]
    adj_ranks = [adj_rank(pog_line) for pog_line in pog_lines]
    colnames = colnames.readlines()
    colnames = [i.strip() for i in colnames]
    n_r = dict()
    for i in range(len(adj_ranks)):
        n_r[colnames[i]] = adj_ranks[i]

    df_tau = pd.DataFrame(columns=n_r.keys(), index=n_r.keys())
    for pair in itertools.product(n_r.keys(), repeat=2):
        a, b = pair
        tau, pval = stats.kendalltau(n_r[a], n_r[b])
        df_tau[a][b] = tau
    print(df_tau)
    df_tau.to_csv(result_dir+'tau_pog.csv')

