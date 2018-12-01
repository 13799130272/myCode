# -*- coding: utf-8 -*-
"""
Created on Tue Nov  6 00:20:59 2018

@author: Tangxinyin
"""



import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import StratifiedShuffleSplit
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import accuracy_score,roc_curve,auc
from sklearn.preprocessing import LabelEncoder
import numpy as np
from sklearn import tree


'''
data description:
   1. Class Name: 3 (L, B, R)
	2. Left-Weight: 5 (1, 2, 3, 4, 5)
	3. Left-Distance: 5 (1, 2, 3, 4, 5)
	4. Right-Weight: 5 (1, 2, 3, 4, 5)
	5. Right-Distance: 5 (1, 2, 3, 4, 5)
'''


#导入数据
names = 'Class Name,Left-Weight,Left_Distance,Right_weight,Right-Distance'.split(',')
dataSet = pd.read_csv('balance.csv',header=None,names=names,index_col=False)

#判断是否有缺失值
groupByLabel = dataSet.groupby('Class Name').size()

#分割数据
split = StratifiedShuffleSplit(test_size=0.3)

for trainIndex,testIndex in split.split(dataSet,dataSet['Class Name']):
    trainSet = dataSet.loc[trainIndex]
    testSet = dataSet.loc[testIndex]

trainTarget = trainSet['Class Name']
testTarget = testSet['Class Name']

trainData = trainSet.drop('Class Name',1)
testData = testSet.drop('Class Name',1)
label = list(dataSet['Class Name'].unique())
#灰度选参
'''
baseTree = DecisionTreeClassifier(criterion='entropy')
paraDict = {'max_depth':[3,4,5,6,7],'min_samples_split':[10,20,30,40,50],'min_samples_leaf':[1,2,3,4,5]}
gridCv = GridSearchCV(baseTree,param_grid=paraDict,scoring='roc_auc',)
gridCv.fit(trainData,trainTarget)
bestParams = gridCv.best_params_
estimatorScore = gridCv.best_score_
result = gridCv.predict(testData)
accuracy = accuracy_score(testTarget,result)
'''
#建立模型
baseTree = DecisionTreeClassifier(criterion='entropy',max_depth=6,min_samples_leaf=1,min_samples_split=20)
baseTree.fit(trainData,trainTarget)
result = baseTree.predict(testData)
accuracy = accuracy_score(testTarget,result)


#绘制特征重要性直方图
dataColNames = trainData.columns.tolist()
featureImportance = pd.Series(baseTree.feature_importances_,index=dataColNames)
featureImportance.plot(kind='bar',rot=30)
plt.title('Feature Importance')


#绘制决策树
import graphviz
import pydotplus

with open('myTree.dot','w') as file:
    file = tree.export_graphviz(baseTree,out_file=file)

dataDot = tree.export_graphviz(baseTree,out_file=None,feature_names=dataColNames,filled=True,class_names=label)
graph = pydotplus.graph_from_dot_data(dataDot)
graph.write_pdf('myTree.pdf')

