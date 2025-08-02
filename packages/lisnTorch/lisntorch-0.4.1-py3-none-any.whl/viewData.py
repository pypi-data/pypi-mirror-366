import matplotlib.pyplot as plt
import pandas 
import pathlib
import re
# todo 其中内容不错 https://zhuanlan.zhihu.com/p/673248419
def sanitize_filename(filename, replace_with='_', max_length=255):
    ILLEGAL_PATTERN = re.compile(r'[<>:"/\\|?*\x00-\x1F\x7F]')
    RESERVED_PATTERN = re.compile(r'^(CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])$', re.IGNORECASE)
    safe_name = ILLEGAL_PATTERN.sub(replace_with, filename).rstrip('.  ')
    if RESERVED_PATTERN.match(safe_name):
        safe_name += '_'
    if len(safe_name) > max_length:
        safe_name = safe_name[:max_length - 4] + '_' + str(hash(safe_name))[:4]
    return safe_name if safe_name else None


def drawHist(df:pandas.DataFrame,saveFilePath:str="./",featureNameList=None,prefix:str="")->None:
     # todo 只能对数值数据
    """
    绘制直方图, 为选中的每一列绘制直方图, 查看数据本身的分布特性
    一图绘制多个子图, 纵轴排列
    saveFilePath: 保存的文件夹路径, 不存在会自动创建,每一个图以列名来命名
    """
    path = pathlib.Path(saveFilePath)
    path.mkdir(exist_ok=True)
    if featureNameList is None:
        featureNameList = df.columns
    for colIdx,featureName in enumerate(featureNameList):
        if not pandas.api.types.is_numeric_dtype(df[featureName]):    # 检查该列列是否为数字类型
            continue
        #数据范围分成 bins 个等宽的区间，然后统计每个区间内数据的频数。
        # n‌频率‌：每个区间内的数据点数量或概率密度。
        # bins‌区间‌：直方图的分组边界，即每个柱状图的范围。
        # patches ‌补丁‌：每个柱状图的图形对象，可用于进一步自定义样式（如颜色、边框等）。
        n, bins, patches = plt.hist(df[featureName].tolist(), color='skyblue', alpha=0.8) #参数bins不写自动默认

        # 设置图表属性
        plt.title(featureName)
        plt.grid()
        plt.xlabel('Value Interval')
        plt.ylabel('Frequency')
        # 显示每个柱的数据个数
        for i in range(len(patches)):
            if n[i]==0:
                continue
            plt.text(patches[i].get_x() + patches[i].get_width() / 2,
                        patches[i].get_height(),
                        str(int(n[i])), ha='center', va='bottom',color="red")
        fileName = sanitize_filename(featureName)
        fileName = fileName if fileName else f"colIdx-{colIdx}"
        plt.savefig(f"{path.absolute()}/{prefix}-{fileName}.png", format="png", bbox_inches="tight", dpi=300)
        plt.close()

    # # todo 参数最大值最小值, 限制轴
    # fig = plt.figure()
    # fig.set_size_inches(2.72,2.72) #放在开头,设置图片大小,2.72正好是doc一列两个图片
    # plt.title(title)
    # plt.xlabel(xlabel)
    # plt.ylabel(ylabel)
    # # plt.ylim(0, 1)#限制y轴范围
    # plt.grid()
    # for lossIdx in range(len(lossName)):
    #     plt.plot(lossList[lossIdx], fmtList[lossIdx],label=lossName[lossIdx])
    # plt.savefig(saveFilePath, format="png", bbox_inches="tight", dpi=300)


def drawHist2D(targetNameList:list, df:pandas.DataFrame,saveFilePath:str="./",featureNameList=None,prefix:str="")->None:
    #  todo 只能对单特征生效
    """
    绘制热图, 为选中的每一列绘制直方图, 查看数据本身的分布特性
    一图绘制多个子图, 纵轴排列
    saveFilePath: 保存的文件夹路径, 不存在会自动创建,每一个图以列名来命名
    featureNameList: 选定的特征名称
    targetNameList:目标名称
    """
    
    path = pathlib.Path(saveFilePath)
    path.mkdir(exist_ok=True)
    # 获取所有特征名称
    if featureNameList is None:
        featureNameList = df.drop(targetNameList,axis=1).columns
    featureDf = df[featureNameList]
    targetDf = df[targetNameList]
    for targetIdx, targetName in  enumerate(targetNameList):
        if not pandas.api.types.is_numeric_dtype(targetDf[targetName]):
            continue
        for colIdx, featureName in enumerate(featureNameList):
            if not pandas.api.types.is_numeric_dtype(featureDf[featureName]):    # 检查该列列是否为数字类型
                continue
            plt.hist2d(featureDf[featureName],targetDf[targetName], color='skyblue') #参数bins不写自动默认
            plt.colorbar()# 显示颜色条
            # 设置图表属性
            plt.title(featureName)
            plt.xlabel(featureName)
            plt.ylabel(targetName)
            filetargetName = sanitize_filename(targetName)
            filetargetName

            fileName = sanitize_filename(f"{targetName}-{featureName}")
            fileName = fileName if fileName else f"target_{targetIdx:02d}-colIdx_{colIdx:02d}"
            plt.savefig(f"{path.absolute()}/{prefix}-{fileName}.png", format="png", bbox_inches="tight", dpi=300)
            plt.close()


# !测试代码
df = pandas.read_csv(
    "D:\\0-研究生学习\\MLExperimentCode\\datas\\jena_climate_2009_2016.csv",
    sep=",",
    header=0,
    index_col=None,
    encoding="utf-8",
    nrows=None,
)
drawHist(df=df,saveFilePath="D:/test/")
drawHist2D(targetNameList=["T (degC)"], df=df,saveFilePath="D:/test/",prefix="exp2")