# 预置
import torch
import numpy as np
import os
import random
import torch.nn as nn
def set_seed(seed:int=12):
    """设置随机数种子"""
    # python自身
    random.seed(seed)
    os.environ["PYTHONHASHSEED"] = str(seed)
    # numpy
    np.random.seed(seed)
    # GPU
    torch.cuda.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)  # 使用多 GPU 时使用
    # cpu
    torch.manual_seed(seed)
    # 限制 Cudnn 在加速过程中涉及到的随机策略
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False

def init_weights(m: nn.Module):
    if type(m) == nn.Linear or type(m) == nn.Conv2d:
        nn.init.xavier_uniform_(m.weight)
    elif type(m) == nn.RNN or nn.LSTM == type(m):
        for name, param in m.named_parameters():
            if "weight_ih" in name:  # 输入到隐藏的权重
                torch.nn.init.xavier_normal_(param)  # 使用Xavier正态分布初始化
            elif "weight_hh" in name:  # 隐藏到隐藏的权重
                torch.nn.init.orthogonal_(param)  # 使用正交初始化
            elif "bias" in name:  # 偏置项
                torch.nn.init.constant_(param, 0.0)  # 设置为0