import numpy as np
import matplotlib.pyplot as plt


def loadSimpdata():
    """
    创建单层决策树的数据集
    Parameters:
        无
    Returns:
        dataMat - 数据矩阵
        classLabels - 数据标签
    """
    dataMat = np.matrix([[1., 2.1],
                         [1.5, 1.6],
                         [1.3, 1.],
                         [1., 1.],
                         [2., 1.]])
    classLabels = [1.0, 1.0, -1.0, -1.0, 1.0]
    return dataMat, classLabels


def showdataSet(dataMat, classLabels):
    """
    数据可视化
    Parameters:
        dataMat - 数据矩阵
        labelMat - 数据标签
    Returns:
        无
    """
    data_plus = []  # 存储正样本
    data_minus = []  # 存储负样本
    for i in range(len(dataMat)):  # 遍历整个数据集
        if classLabels[i] > 0:  # 如果标签的值大于0
            data_plus.append(dataMat[i])  # 将这个样本添加到正样本数据集
        else:
            data_minus.append(dataMat[i])  # 否则将这个样本添加到负样本数据集
    data_plus_np = np.array(data_plus)  # 将正样本和负样本的数据集转化为np.arrays(可以转置便于操作)
    data_minus_np = np.array(data_minus)
    plt.scatter(np.transpose(data_plus_np)[0], np.transpose(data_plus_np)[1])  # 根据其不同的取值进行画图
    plt.scatter(np.transpose(data_minus_np)[0], np.transpose(data_minus_np)[1])
    plt.show()


def stumpClassify(dataMatrix, dimen, threshVal, thresIneq):  # 单层决策树进行分类
    """
    单层决策树分类函数
    Parameters:
        dataMatrix - 数据矩阵
        dimen - 第dimen列，也就是第几个特征
        threshVal - 阈值
        threshIneq - 标志
    Returns:
        retArray - 分类结果
    """
    retArray = np.ones((np.shape(dataMatrix)[0], 1))  # 初始化retArray全都是1, 长度与整个数据集的长度相同(初始时默认全为1类)
    if thresIneq == 'lt':  # 如果标签是小于号的话
        retArray[dataMatrix[:, dimen] <= threshVal] = -1.0  # 检查在给定的判断阈值上的所有样本, 若其值小于阈值,则判断为-1类别
    else:
        retArray[dataMatrix[:, dimen] > threshVal] = -1.0  # 否则在大于时才判断为-1类别
    return retArray


def buildStump(dataArr, classLabels, D):
    """
    找到数据集上最佳的单层决策树
    Parameters:
        dataArr - 数据矩阵
        classLabels - 数据标签
        D - 样本权重
    Returns:
        bestStump - 最佳单层决策树信息
        minError - 最小误差
        bestClasEst - 最佳的分类结果
    """
    dataMatrix = np.mat(dataArr)  # 将给定给定数据集转换为np的矩阵
    labelMat = np.mat(classLabels).T  # 同理处理标签的矩阵(列向量化)
    m, n = np.shape(dataMatrix)  # 返回数据矩阵的数据集大小和特征维度
    numSteps = 10.0  # 总步数
    bestStump = {}  # 初始化最佳的决策树桩(字典类型)
    bestClasEst = np.mat(np.zeros((m, 1)))
    minError = float('inf')  # 最小误差初始化为无穷大
    for i in range(n):  # 遍历所有特征
        rangeMin = dataMatrix[:, i].min()
        rangeMax = dataMatrix[:, i].max()  # 找到当前特征中最小的值和最大值
        stepSize = (rangeMax - rangeMin) / numSteps  # 计算步长
        for j in range(-1, int(numSteps) + 1):
            for inequal in ['lt', 'gt']:  # 大于和小于的情况，均遍历。lt:less than，gt:greater than
                threshVal = (rangeMin + float(j) * stepSize)  # 计算阈值(阈值就是当前决策树的分类位置)
                predictedVals = stumpClassify(dataMatrix, i, threshVal, inequal)  # 计算分类结果
                errArr = np.mat(np.ones((m, 1)))  # 初始化误差矩阵
                errArr[predictedVals == labelMat] = 0  # 分类正确的,赋值为0
                weightedError = D.T * errArr  # 计算误差(计算错误的所有样本权重的和)
                print("split: dim %d, thresh %.2f, thresh ineqal: %s, the weighted error is %.3f" % (
                    i, threshVal, inequal, weightedError))
                if weightedError < minError:  # 找到误差最小的分类方式
                    minError = weightedError  # 更新最小误差
                    bestClasEst = predictedVals.copy()  # 最佳分类情况
                    bestStump['dim'] = i  # 标记第n维度
                    bestStump['thresh'] = threshVal  # 标记当前决策树的分类线的位置
                    bestStump['ineq'] = inequal  # 标记是大于还是小于(大于分类线是判断为1还是小于的时候判断为1)
    return bestStump, minError, bestClasEst


def adaBoostTrainDS(dataArr, classLabels, numIt=40):
    """
    使用AdaBoost算法提升弱分类器性能
    Parameters:
        dataArr - 数据矩阵
        classLabels - 数据标签
        numIt - 最大迭代次数
    Returns:
        weakClassArr - 训练好的分类器
        aggClassEst - 类别估计累计值
    """
    weakClassArr = []
    m = np.shape(dataArr)[0]
    D = np.mat(np.ones((m, 1)) / m)  # 初始化权重
    aggClassEst = np.mat(np.zeros((m, 1)))
    for i in range(numIt):
        bestStump, error, classEst = buildStump(dataArr, classLabels, D)  # 构建单层决策树
        # print("D:",D.T)
        alpha = float(0.5 * np.log((1.0 - error) / max(error, 1e-16)))  # 计算弱学习算法权重alpha,使error不等于0,因为分母不能为0
        bestStump['alpha'] = alpha  # 存储弱学习算法权重
        weakClassArr.append(bestStump)  # 存储单层决策树
        # print("classEst: ", classEst.T)
        expon = np.multiply(-1 * alpha * np.mat(classLabels).T, classEst)  # 计算e的指数项
        D = np.multiply(D, np.exp(expon))
        D = D / D.sum()  # 根据样本权重公式，更新样本权重
        # 计算AdaBoost误差，当误差为0的时候，退出循环
        aggClassEst += alpha * classEst  # 计算类别估计累计值
        # print("aggClassEst: ", aggClassEst.T)
        aggErrors = np.multiply(np.sign(aggClassEst) != np.mat(classLabels).T, np.ones((m, 1)))  # 计算误差
        errorRate = aggErrors.sum() / m
        # print("total error: ", errorRate)
        if errorRate == 0.0: break  # 误差为0，退出循环
    return weakClassArr, aggClassEst


def adaClassify(datToClass, classifierArr):
    """
    AdaBoost分类函数
    Parameters:
        datToClass - 待分类样例
        classifierArr - 训练好的分类器
    Returns:
        分类结果
    """
    dataMatrix = np.mat(datToClass)
    m = np.shape(dataMatrix)[0]
    aggClassEst = np.mat(np.zeros((m, 1)))
    for i in range(len(classifierArr)):  # 遍历所有分类器，进行分类
        classEst = stumpClassify(dataMatrix, classifierArr[i]['dim'], classifierArr[i]['thresh'],
                                 classifierArr[i]['ineq'])
        aggClassEst += classifierArr[i]['alpha'] * classEst
        print(aggClassEst)
    return np.sign(aggClassEst)


dataArr, labelArr = loadSimpdata()