import collections
import itertools

import pandas as pd

# 数据清理
originData = pd.read_csv(r'src\step1\tag_cooccurrence.csv')
numOfData = len(originData)
tagsList = []
for i in range(numOfData):
    tagsStr = originData.ix[i, 'tags'].split(',')
    tagsList.append(tagsStr)

# print(tagsList)
data = tagsList
support = int(0.01 * numOfData)

CountItem = collections.defaultdict(int)
for line in data:
    for item in line:
        CountItem[item] += 1

a = sorted(CountItem.items(), key=lambda x: x[1], reverse=True)

for i in range(len(a)):
    if a[i][1] < support:
        a = a[:i]
        break

for i in range(numOfData):
    data[i] = [char for char in data[i] if CountItem[char] >= support]
    data[i] = sorted(data[i], key=lambda x: CountItem[x], reverse=True)


class node():
    def __init__(self, val, char):
        self.val = val
        self.char = char
        self.children = {}
        self.next = None
        self.father = None
        self.visit = 0
        self.nodeLink = collections.defaultdict()
        self.nodeLink1 = collections.defaultdict()


class FPTree():
    def __init__(self):
        self.root = node(-1, 'root')
        self.frequentItem = collections.defaultdict(int)
        self.res = []

    def buildTree(self, data):
        for line in data:
            root = self.root
            for item in line:
                if item not in root.children.keys():
                    root.children[item] = node(1, item)
                    root.children[item].father = root
                else:
                    root.children[item].val += 1
                root = root.children[item]

                if item in self.root.nodeLink.keys():
                    if root.visit == 0:
                        self.root.nodeLink1[item].next = root
                        self.root.nodeLink1[item] = self.root.nodeLink1[item].next
                        root.visit = 1
                else:
                    self.root.nodeLink[item] = root
                    self.root.nodeLink1[item] = root
                    root.visit = 1

        return self.root

    def isSinglePath(self, root):
        if not root:
            return True
        if not root.children:
            return True

        a = list(root.children.values())
        if len(a) > 1:
            return False
        else:
            for value in root.children.values():
                if self.isSinglePath(value) == False:
                    return False
            return True

    def FP_growth(self, tree, a, headTable):

        if self.isSinglePath(tree):
            root, temp = tree, []
            while root.children:
                for child in root.children.values():
                    temp.append((child.char, child.val))
                    root = child

            ans = []
            for i in range(1, len(temp) + 1):
                ans += list(itertools.combinations(temp, i))

            for item in ans:
                myChar = [char[0] for char in item] + a
                myCount = min([count[1] for count in item])
                if myCount >= support:
                    self.res.append([myChar, myCount])

        else:
            # root = tree

            headTable.reverse()

            for (child, count) in headTable:
                b = [child] + a
                self.res.append([b, count])
                tmp = tree.nodeLink[child]
                data = []

                while tmp:
                    tmpUp = tmp
                    res = [[], tmpUp.val]

                    while tmpUp.father:
                        res[0].append(tmpUp.char)
                        tmpUp = tmpUp.father

                    res[0] = res[0][::-1]
                    data.append(res)
                    tmp = tmp.next

                CountItem = collections.defaultdict(int)
                for [tmp, count] in data:
                    for i in tmp[:-1]:
                        CountItem[i] += count

                for i in range(len(data)):
                    data[i][0] = [char for char in data[i][0] if CountItem[char] >= support]
                    data[i][0] = sorted(data[i][0], key=lambda x: CountItem[x], reverse=True)

                root = node(-1, 'root')
                for [tmp, count] in data:

                    tmpRoot = root

                    for item in tmp:

                        if item in tmpRoot.children.keys():
                            tmpRoot.children[item].val += count

                        else:
                            tmpRoot.children[item] = node(count, item)
                            tmpRoot.children[item].father = tmpRoot
                        tmpRoot = tmpRoot.children[item]

                        if item in root.nodeLink.keys():
                            if tmpRoot.visit == 0:
                                root.nodeLink1[item].next = tmpRoot
                                root.nodeLink1[item] = root.nodeLink1[item].next
                                tmpRoot.visit = 1
                        else:
                            root.nodeLink[item] = tmpRoot
                            root.nodeLink1[item] = tmpRoot
                            tmpRoot.visit = 1
                if root:
                    newHeadTable = sorted(CountItem.items(), key=lambda x: x[1], reverse=True)

                    for i in range(len(newHeadTable)):
                        if newHeadTable[i][1] < support:
                            newHeadTable = newHeadTable[:i]
                            break
                    self.FP_growth(root, b, newHeadTable)


'''
obj = FPTree()
root = obj.buildTree(data)
obj.FP_growth(root, [], a)

numOfFreSet = len(obj.res)
sortedFreSet = sorted(obj.res, key=lambda x: len(x[0]), reverse=True)

for i in range(numOfFreSet):
    if len(sortedFreSet[i][0]) <= 1:
        sortedFreSet = sortedFreSet[:i]
        break

# for i in range(numOfFreSet):
items = sortedFreSet[0][0]
sup = sortedFreSet[0][1]
itemList = []
for i in range(1,len(items)):
    itemList += list(itertools.combinations(items, i))
print(itemList)
dict = {}
for i in range(len(itemList)):
    count = 0
    for j in range(numOfData):
        if set(itemList[i]) in set(data[j]):
            count += 1
    dict[itemList[i]] = count

data_1 = data[0]
print(set(data_1))
print(set(itemList[0]))
'''

import fp_growth as fpg

fre = fpg.find_frequent_itemsets(data, 0.01, True)
print(list(fre))
