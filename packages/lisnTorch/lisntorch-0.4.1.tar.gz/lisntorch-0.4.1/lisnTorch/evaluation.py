# 用于评价
# 评价模型大小用 ResourceConsumption
# 输出误差图片用 drawLossPicture
import pygame
import matplotlib.pyplot as plt
import torch
import torch.nn as nn
import os
from torchsummary import summary
from thop import profile
from thop import clever_format
if os.name == 'nt':
    plt.rcParams['font.family'] = 'SimHei'  # 替换为你选择的字体  
else:
    plt.rcParams['font.family'] = 'WenQuanYi Micro Hei'  # 替换为你选择的字体

def ResourceConsumption(net: nn.Module , input_data: tuple = tuple(),isRNN:bool=False,device:str="cpu") -> str:
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
                device=device
            )
    # 适合多参数模型
    flops,params = profile( net, inputs=input_data )  # 看源码 自定义模型的inputs可能有多个, 所以用个turple
    flops,params = clever_format([flops, params], "%.3f")
    return f"{summary_info}\n FLOPs:{flops},  params num:{params}"


def drawLinePicture(savePathName,lineList:list=[],lineNameList:list=[],fmtList:list=[],title="",xlabel="epochs",ylabel="value",pictureSize:tuple=(2.72,2.72))->None:
    """
    saveFilePath: 保存文件名, 绝对路径,文件格式为png
    lineList: 需要画线的表
    lineName: 每种损失的名字
    fmt:定义了基本格式，如标记、线条样式和颜色。 https://www.runoob.com/matplotlib/matplotlib-marker.html 
    title: 标题
    xlabel:横轴名
    ylabel: 纵轴名
    """
    assert len(lineList) == len(lineNameList)
    assert len(lineList) == len(fmtList)
    assert len(pictureSize) == 2
    # todo 参数最大值最小值, 限制轴
    fig = plt.figure()
    fig.set_size_inches(*pictureSize) #放在开头,设置图片大小,2.72正好是doc一列两个图片
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    # plt.ylim(0, 1)#限制y轴范围
    plt.grid()
    for lineIdx in range(len(lineList)):
        plt.plot(lineList[lineIdx], fmtList[lineIdx],label=lineNameList[lineIdx])
    plt.legend()#一定要放在所有plot后面
    plt.savefig(savePathName, format="png", bbox_inches="tight", dpi=300)
    plt.close()

def finishAlarm(MP3Path:str="",repeatNum:int=1):
    """
    运行结束提示
    """
    print("                            _ooOoo_                     ")
    print("                           o8888888o                    ")
    print("                           88  .  88                    ")
    print("                           (| -_- |)                    ")
    print("                            O\\ = /O                    ")
    print("                        ____/`---'\\____                ")
    print("                      .   ' \\| |// `.                  ")
    print("                       / \\||| : |||// \\               ")
    print("                     / _||||| -:- |||||- \\             ")
    print("                       | | \\\\\\ - /// | |             ")
    print("                     | \\_| ''\\---/'' | |              ")
    print("                      \\ .-\\__ `-` ___/-. /            ")
    print("                   ___`. .' /--.--\\ `. . __            ")
    print("                ."" '< `.___\\_<|>_/___.' >'"".         ")
    print("               | | : `- \\`.;`\\ _ /`;.`/ - ` : | |     ")
    print("                 \\ \\ `-. \\_ __\\ /__ _/ .-` / /      ")
    print("         ======`-.____`-.___\\_____/___.-`____.-'====== ")
    print("                            `=---='  ")
    print("                                                        ")
    print("         .............................................  ")
    pygame.init()

    for i in range(repeatNum):
        pygame.mixer.music.load(MP3Path)  
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():  # 等待音乐播放完毕
            pygame.time.Clock().tick(10)

# todo cpu总时间,gpu总时间,现实时间

# !测试代码
# if __name__ == "__main__":
#     x1 = numpy.random.randn(10)
#     x2 = numpy.random.randn(10)
#     # drawLossPicture("D:\\test1.png",lossList=[x1,x2],lossName=["x1","x2"],fmtList=["r-","g-."])
#     # drawLossPicture("D:\\test2.png",lossList=[x1,x2],lossName=["x1","x2"],fmtList=["r-","g-."])
    
    
    
