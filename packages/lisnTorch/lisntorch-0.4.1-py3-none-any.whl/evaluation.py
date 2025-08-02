# 用于评价
# 评价模型大小用 ResourceConsumption
# 输出误差图片用 drawLossPicture

import matplotlib.pyplot as plt
import torch
import torch.nn as nn

from torchsummary import summary
from thop import profile
from thop import clever_format

def ResourceConsumption(net: nn.Module , input_data: tuple = tuple(),isRNN:bool=False) -> str:
    """input_data是一个能运行的批次数据,所有元素均为tensor,第0元素的 0维度是批次"""
    if net is None:
        return "net is None"
    summary_info = ""
    #  todo input_size只能对应单个输入,多输入会报错
    if not isRNN:
        if len(input_data) == 1:
            shape = input_data[0].shape
            input_size = list(shape)
            input_size[0] = 1
            summary_info = summary(
                net, batch_size=shape[0], input_size=tuple(input_size),
                device="cpu"
            )
    # 适合多参数模型
    flops,params = profile( net, inputs=input_data )  # 看源码 自定义模型的inputs可能有多个, 所以用个turple
    flops,params = clever_format([flops, params], "%.3f")
    return f"{summary_info}\n FLOPs:{flops},  params num:{params}"


def drawLossPicture(savePathName,lossList:list=[],lossName:list=[],fmtList:list=[],title="",xlabel="epochs",ylabel="loss",)->None:
    """
    saveFilePath: 保存文件名, 绝对路径,文件格式为png
    lossList: 损失值, 元素应该为tuple或者list, 每个元素均为一个损失列表, 与lossName,fmt等长
    lossName: 每种损失的名字
    fmt:定义了基本格式，如标记、线条样式和颜色。 https://www.runoob.com/matplotlib/matplotlib-marker.html 
    title: 标题
    xlabel:横轴名
    ylabel: 纵轴名
    """

    # todo 参数最大值最小值, 限制轴
    fig = plt.figure()
    fig.set_size_inches(2.72,2.72) #放在开头,设置图片大小,2.72正好是doc一列两个图片
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    # plt.ylim(0, 1)#限制y轴范围
    plt.grid()
    for lossIdx in range(len(lossName)):
        plt.plot(lossList[lossIdx], fmtList[lossIdx],label=lossName[lossIdx])
    plt.savefig(savePathName, format="png", bbox_inches="tight", dpi=300)
    plt.close()


# !测试代码
# if __name__ == "__main__":
#     x1 = numpy.random.randn(10)
#     x2 = numpy.random.randn(10)
#     # drawLossPicture("D:\\test1.png",lossList=[x1,x2],lossName=["x1","x2"],fmtList=["r-","g-."])
#     # drawLossPicture("D:\\test2.png",lossList=[x1,x2],lossName=["x1","x2"],fmtList=["r-","g-."])
    
    
    
