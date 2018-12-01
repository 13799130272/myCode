import json
import time

import requests

# **************************************************************************************
# 爬知乎话题：如何看待杨超越在七度空间上的一番演讲？
# 由于爬话题内容不需要登陆，所以只要找到真实地址，用JSON解析便可以得到数据
# **************************************************************************************

# 创建文档，模式为“追加”，编码方式为utf-8
file = open('zhihuData.txt', 'a', encoding='utf-8')

# 由于不知道一共有多少页，假设抓取前1000页，后面会有判定条件退出循环

for i in range(1, 1000):
    print(i, 'begin')

    # 定制网页、定制请求头
    url = 'https://www.zhihu.com/api/v4/questions/303589746/answers?include=data[*].is_normal,admin_closed_comment,reward_info,is_collapsed,annotation_action,annotation_detail,collapse_reason,is_sticky,collapsed_by,suggest_edit,comment_count,can_comment,content,editable_content,voteup_count,reshipment_settings,comment_permission,created_time,updated_time,review_info,relevant_info,question,excerpt,relationship.is_authorized,is_author,voting,is_thanked,is_nothelp,is_labeled;data[*].mark_infos[*].url;data[*].author.follower_count,badge[*].topics&offset=' + str(
        i) + '&limit=5&sort_by=default'
    loginHeader = {'Host': 'www.zhihu.com',
                   'origin': 'https://www.zhihu.com',
                   'Referer': 'https://www.zhihu.com/question/303589746',
                   'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:63.0) Gecko/20100101 Firefox/63.0'}

    # 请求连接
    r = requests.get(url, headers=loginHeader)

    # 解析放回的JSON数据,JSON模块将其转化为字典
    jsonData = json.loads(r.text)

    # 判断是否退出
    isEnd = jsonData['paging']['is_end']

    # 这里是回答所在的数据
    data = jsonData['data']
    for j in range(len(data)):
        file.write(data[j]['content'])
        file.write('\n')
        file.write('\n')

    # 如果isEnd==True，退出循环
    if isEnd:
        print(i, 'end')
        break
    time.sleep(1.5)
    print(i, 'end')

# 关闭文件
file.close()
