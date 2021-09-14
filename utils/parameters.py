import argparse


def pretrain_parser():
    parser = argparse.ArgumentParser(description='pretrain parser')
    parser.add_argument('--img', type=str, help='name of the image directory')
    parser.add_argument('--name', type=str, help='model & annotated directory name')

    return parser.parse_args()
def siCluster_parser():
    parser = argparse.ArgumentParser(description='siCluster parser')
    parser.add_argument('--lr', default=1e-4, type=float, help='learning rate')
    parser.add_argument('--epochs', type=int, default=20, help='number of total epochs to run') ##20
    parser.add_argument('--batch', default=32, type=int, help='mini-batch size') ##32
    parser.add_argument('--momentum', default=0.9, type=float, help='momentum')
    parser.add_argument('--seed', type=int, default=31, help='random seed')
    parser.add_argument('--nmb_cluster', '--k', type=int, default = 50, help='number of cluster for k-means')
    parser.add_argument('--name', type=str, help='model & annotated directory name')
    parser.add_argument('--img', type=str, help='name of the image directory')
  
    return parser.parse_args()

def siScore_parser():
    parser = argparse.ArgumentParser(description='siScore parser')
    parser.add_argument('--lr', '--learning-rate', default=1e-4, type=float, metavar='LR', help='learning rate')#1e-3
    parser.add_argument('--batch-sz', default=16, type=int, help='batch size') #16
    parser.add_argument('--epochs', default=200, type=int, help='total epochs') #200
    parser.add_argument('--load', dest='load', action='store_true', help='load trained model')
    parser.add_argument('--modelurl', type=str, help='model path')
    parser.add_argument('--seed', default=1567010775, type=int, help='random seed')    
    parser.add_argument('--lamb', default=30, type=int, help='lambda parameter for differentiable ranking')
    parser.add_argument('--alpha', default=0, type=int, help='alpha parameter for differentiable ranking')
    parser.add_argument('--dir_name', type=str, default='', help='directory name for cluster data')
    parser.add_argument('--cluster_num', default=9, type=int, help='number of clusters')
    parser.add_argument('--model', type=str, help='Model name') 
    parser.add_argument('--graph_config', type=str, help='graph config path')
    parser.add_argument('--name', type=str, help='model & annotated directory name')
    parser.add_argument('--img', type=str, help='name of the image directory')   
    return parser.parse_args()

def extract_cluster_parser():
    parser = argparse.ArgumentParser(description='extract_cluster parser')
    parser.add_argument('--city_cnum', default=911, type=int, help='number of city clusters')
    parser.add_argument('--rural_cnum', default=111, type=int, help='number of rural clusters')
    parser.add_argument('--name', type=str, help='model & annotated directory name')
    parser.add_argument('--img', type=str, help='name of the image directory')   
    return parser.parse_args()

