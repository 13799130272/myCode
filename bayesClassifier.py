# coding:utf-8
import random

import numpy as np


def loadDataSet():
    postingList = [['my', 'dog', 'has', 'flea', 'problems', 'help', 'please'],
                   ['maybe', 'not', 'take', 'him', 'to', 'dog', 'park', 'stupid'],
                   ['my', 'dalmation', 'is', 'so', 'cute', 'I', 'love', 'him'],
                   ['stop', 'posting', 'stupid', 'worthless', 'garbage'],
                   ['mr', 'licks', 'ate', 'my', 'steak', 'how', 'to', 'stop', 'him'],
                   ['quit', 'buying', 'worthless', 'dog', 'food', 'stupid']]
    classVec = [0, 1, 0, 1, 0, 1]  # 1 is abusive, 0 not
    return postingList, classVec


def createVocabList(dataSet):
    vocabSet = set([])
    for document in dataSet:
        vocabSet = vocabSet | set(document)
    return list(vocabSet)


def setOfWordsToVec(vocabList, inputSet):
    returnVec = [0] * len(vocabList)
    for word in inputSet:
        if word in vocabList:
            returnVec[vocabList.index(word)] = 1
        else:
            print('the word: %s is not in my Vocabulary!' % word)
    return returnVec


def bagOfWordsToVecMN(vocabList, inputSet):
    returnVec = [0] * len(vocabList)
    for word in inputSet:
        if word in vocabList:
            returnVec[vocabList.index(word)] += 1
        return returnVec


def trainNB0(trainMatrix, trainCategory):
    numTrainDocs = len(trainMatrix)
    numWords = len(trainMatrix[0])
    pAbusive = sum(trainCategory) / float(numTrainDocs)
    p0Num = np.ones(numWords)
    p1Num = np.ones(numWords)
    p0Denom = 2.0
    p1Denom = 2.0
    for i in range(numTrainDocs):
        if trainCategory[i] == 1:
            p1Num += trainMatrix[i]
            p1Denom += sum(trainMatrix[i])
        else:
            p0Num += trainMatrix[i]
            p0Denom += sum(trainMatrix[i])
    p1Vect = np.log(p1Num / p1Denom)
    p0Vect = np.log(p0Num / p0Denom)
    return p0Vect, p1Vect, pAbusive


def classifyNB(vecToClassify, p0Vec, p1Vec, pClass1):
    p1 = sum(vecToClassify * p1Vec) + np.log(pClass1)
    p0 = sum(vecToClassify * p0Vec) + np.log(1.0 - pClass1)
    if p1 > p0:
        return 1
    else:
        return 0


def testingNB():
    listOfPosts, listClasses = loadDataSet()
    myVocabList = createVocabList(listOfPosts)
    trainMat = []
    for postinDoc in listOfPosts:
        trainMat.append(setOfWordsToVec(myVocabList, postinDoc))
    p0V, p1V, pAb = trainNB0(np.array(trainMat), np.array(listClasses))
    testEntry = ['love', 'my', 'dalmation']
    thisDoc = np.array(setOfWordsToVec(myVocabList, testEntry))
    print(testEntry, 'classified as: ', classifyNB(thisDoc, p0V, p1V, pAb))
    testEntry = ['stupid', 'garbage']
    thisDoc = np.array(setOfWordsToVec(myVocabList, testEntry))
    print(testEntry, 'classified as: ', classifyNB(thisDoc, p0V, p1V, pAb))


def textParse(bigString):
    import re
    listOfTokens = re.split(r'\W*', bigString)
    return [tok.lower() for tok in listOfTokens if len(tok) > 2]


def spamTest(seed):
    random.seed(int(seed))
    docList = []
    classList = []
    fullText = []
    for i in range(1, 26):
        spamFile = open('spam/%d.txt' % i, errors='ignore').readlines()
        fileList = []
        for i in range(len(spamFile)):
            listData = textParse(spamFile[i].strip())
            fileList.extend(listData)
        docList.append(fileList)
        fullText.extend(fileList)
        classList.append(1)
        hamFile = open('ham/%d.txt' % i, errors='ignore').readlines()
        fileList = []
        for i in range(len(hamFile)):
            listData = textParse(hamFile[i].strip())
            fileList.extend(listData)
        docList.append(fileList)
        fullText.extend(fileList)
        classList.append(0)
    vocabList = createVocabList(docList)
    trainingSet = list(range(50))
    testSet = []
    for i in range(10):
        randIndex = int(random.uniform(0, len(trainingSet)))
        testSet.append(trainingSet[randIndex])
        del trainingSet[randIndex]
    trainMat = []
    trainClasses = []
    for docIndex in trainingSet:
        trainMat.append(setOfWordsToVec(vocabList, docList[docIndex]))
        trainClasses.append(classList[docIndex])
    p0V, p1V, pSpam = trainNB0(np.array(trainMat), np.array(trainClasses))
    errorCount = 0
    for docIndex in testSet:
        wordVector = setOfWordsToVec(vocabList, docList[docIndex])
        print('the original class is: %s, the predicted class is: %s. ' % (
            classifyNB(np.array(wordVector), p0V, p1V, pSpam), classList[docIndex]))
        if classifyNB(np.array(wordVector), p0V, p1V, pSpam) != classList[docIndex]:
            errorCount += 1
    print('the error rate is: ', float(errorCount) / len(testSet))
    return float(errorCount) / len(testSet)


def calcMostFreq(vocabList, fullText, numToRe):
    freqDict = {}
    for token in vocabList:
        freqDict[token] = fullText.count(token)
    sortedFreq = sorted(freqDict.items(), key=lambda x: x[1], reverse=True)
    return sortedFreq[:int(numToRe)]


def localWords(feed_1, feed_0):
    docList = []
    classList = []
    fullText = []
    minLen = min(len(feed_1['entries']), len(feed_0['entries']))
    for i in range(minLen):
        wordList = textParse(feed_1['entries'][i]['summary'])
        docList.append(wordList)
        fullText.extend(wordList)
        classList.append(1)
        wordList = textParse(feed_0['entries'][i]['summary'])
        docList.append(wordList)
        fullText.extend(wordList)
        classList.append(0)
    vocabList = createVocabList(docList)
    '''
    with open('stopWord.txt') as file:
        fileData = []
        for data in file.readlines():
            fileData.extend(data.strip())
        for stopWord in fileData:
            if stopWord in vocabList:
                vocabList.remove(stopWord)
    file.close()
    '''
    topWords = calcMostFreq(vocabList, fullText, 5)
    for pairW in topWords:
        if pairW[0] in vocabList:
            vocabList.remove(pairW[0])

    trainingSet = list(range(minLen))

    testSet = []
    for i in range(10):
        randIndex = int(random.uniform(0, len(trainingSet)))
        testSet.append(trainingSet[randIndex])
        del trainingSet[randIndex]
    trainMat = []
    trainClasses = []
    for docIndex in trainingSet:
        trainMat.append(bagOfWordsToVecMN(vocabList, docList[docIndex]))
        trainClasses.append(classList[docIndex])
    p0V, p1V, pSpam = trainNB0(np.array(trainMat), np.array(trainClasses))
    errorCount = 0
    for docIndex in testSet:
        wordVector = bagOfWordsToVecMN(vocabList, docList[docIndex])
        if classifyNB(np.array(wordVector), p0V, p1V, pSpam) != classList[docIndex]:
            errorCount += 1
    print('the error rate is: %f' % (float(errorCount) / len(testSet)))
    return vocabList, p0V, p1V


def getTopWprds(ny, sf):
    vocabList, p0V, p1V = localWords(ny, sf)
    topNY = []
    topSF = []
    for i in range(len(p0V)):
        if p0V[i] > -6.0:
            topSF.append((vocabList[i], p0V[i]))
        if p1V[i] > -6.0:
            topNY.append((vocabList[i], p1V[i]))
    sortedSF = sorted(topSF, key=lambda pair: pair[1], reverse=True)
    print('SF**' * 14)
    for item in sortedSF:
        print(item[0])
    sortedNY = sorted(topNY, key=lambda pair: pair[1], reverse=True)
    print('NY**' * 14)
    for item in sortedNY:
        print(item[0])


if __name__ == '__main__':
    import feedparser

    rss_1 = 'http://www.nasa.gov/rss/dyn/image_of_the_day.rss'
    rss_2 = 'http://www.cppblog.com/kevinlynx/category/6337.html/rss'
    feed_0 = feedparser.parse(rss_1)
    feed_1 = feedparser.parse(rss_2)
    print(feed_1['entries'][1]['summary'])
    '''
    getTopWprds(feed_0, feed_1)
'''
