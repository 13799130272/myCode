# coding:utf-8
from math import log
import operator
from treePlotter import retrieveTree, createPlot
from trees import transform
import pandas as pd

fileName = 'balance.csv'
columnsName_1 = (
    'Class Name', 'Left-Weight', 'Left-Distance', 'Right-Weight', 'Right-Distance')
columnsName_2 = (
    'Left-Weight', 'Left-Distance', 'Right-Weight', 'Right-Distance', 'Class')
numOfTrainSet = 325
labelNum = 0
attrDict = {'Class Name': 0, 'Left-Weight': 1, 'Left-Distance': 2, 'Right-Weight': 3, 'Right-Distance': 4}


def importData(data, header, numOfTrainSet):
    numOfData = len(data)
    trainSet = data[:numOfTrainSet]
    testSet = data[numOfTrainSet:]
    dataLabels = trainSet.iloc[0:, 1:].columns.values.tolist()
    trainSetList = []
    testSetList = []
    for i in range(numOfTrainSet):
        trainVec = trainSet.iloc[i, :].tolist()
        trainSetList.append(trainVec)
    for j in range(numOfData - numOfTrainSet):
        testVec = testSet.iloc[j, :].tolist()
        testSetList.append(testVec)
    return trainSetList, testSetList, dataLabels


def calcShannonEnt(dataSet):
    numEntries = len(dataSet)
    labelCounts = {}
    for featVec in dataSet:
        currentLabel = featVec[-1]
        if currentLabel not in list(labelCounts.keys()):
            labelCounts[currentLabel] = 0
        labelCounts[currentLabel] += 1
    shannonEnt = 0.0
    for key in labelCounts:
        prob = float(labelCounts[key]) / numEntries
        shannonEnt -= prob * log(prob, 2)
    return shannonEnt


def createDataSet():
    dataSet = [[1, 1, 'yes'], [1, 1, 'yes'], [1, 0, 'no'], [0, 1, 'no'], [0, 1, 'no']]
    labels = ['no surfacing', 'flippers']
    return dataSet, labels


def splitDataSet(dataSet, axis, value):
    retDataSet = []
    for featVec in dataSet:
        if featVec[axis] == value:
            reducedFeatVec = featVec[:axis]
            reducedFeatVec.extend(featVec[axis + 1:])
            retDataSet.append(reducedFeatVec)
    return retDataSet


def chooseBestFeatureToSplit(dataSet):
    numFeatures = len(dataSet[0]) - 1
    baseEntropy = calcShannonEnt(dataSet)
    bestInfoGain = 0.0
    bestFeature = -1
    for i in range(numFeatures):
        featList = [example[i] for example in dataSet]
        uniqueVals = set(featList)
        newEntropy = 0.0
        for value in uniqueVals:
            subDataSet = splitDataSet(dataSet, i, value)
            prob = len(subDataSet) / float(len(dataSet))
            newEntropy += prob * calcShannonEnt(subDataSet)
        infoGain = baseEntropy - newEntropy
        if infoGain > bestInfoGain:
            bestInfoGain = infoGain
            bestFeature = i
    return bestFeature


def majorityCnt(classList):
    classCount = {}
    for vote in classList:
        if vote not in list(classCount.keys()):
            classCount[vote] = 0
        classCount[vote] += 1
        sortedClassCount = sorted(classCount.item(), key=operator.itemgetter(1), reverse=True)
        return sortedClassCount[0][0]


def createTree(dataSet, labels):
    classList = [example[-1] for example in dataSet]
    if classList.count(classList[0]) == len(classList):
        return classList[0]
    if len(dataSet[0]) == 1:
        return majorityCnt(classList)
    bestFeat = chooseBestFeatureToSplit(dataSet)
    bestFeatLabel = labels[bestFeat]
    myTree = {bestFeatLabel: {}}
    del (labels[bestFeat])
    featValues = [example[bestFeat] for example in dataSet]
    uniqueVals = set(featValues)
    for value in uniqueVals:
        subLabels = labels[:]
        myTree[bestFeatLabel][value] = createTree(splitDataSet(dataSet, bestFeat, value), subLabels)
    return myTree


def classify(inputTree, featLables, testVec):
    classLabel = ''
    firstStr = list(inputTree.keys())[0]
    secondDict = inputTree[firstStr]
    featIndex = featLables.index(firstStr)
    for key in secondDict.keys():
        if testVec[featIndex] == key:
            if type(secondDict[key]).__name__ == 'dict':
                classLabel = classify(secondDict[key], featLables, testVec)
            else:
                classLabel = secondDict[key]
    return classLabel


def errorRate(myTree, featLabels, testSet):
    numOfTestData = len(testSet)
    count = 0
    for i in range(numOfTestData):
        testVec = testSet[i]
        testClass = testVec[-1]
        testResult = classify(myTree, featLabels, testVec)
        print('No.%d, the origin class is %s, the test class is %s.' % (i + 1, testClass, testResult))
        if testClass != testResult:
            count += 1
    errorRate = float(count) / numOfTestData
    print('The error rate is %f' % errorRate)


def storeTree(inputTree, fileName):
    import pickle
    fw = open(fileName, 'wb')
    pickle.dump(inputTree, fw)
    fw.close()


def grabTree(fileName):
    import pickle
    fr = open(fileName, 'rb')
    return pickle.load(fr)


if __name__ == '__main__':
    originData = transform(fileName, columnsName_1, 'Class Name', 'Name of Class')
    trainSet, testSet, label = importData(originData, columnsName_2, numOfTrainSet)
    label_2 = label[:]
    myTree = createTree(trainSet, label)
    print(myTree)
    errorRate(myTree, label_2, trainSet)
