# coding=utf-8
import json
import time

import requests
from PIL import Image
from bs4 import BeautifulSoup

# **********************************************用Python登陆豆瓣爬取影评***************************************************
"""
首先进行豆瓣的模拟登陆，通过抓包可以知道，当没有要求输入验证码时，豆瓣登陆传递的表单数据有：form_email、form_password、 login、redir、source、remember
如果要求输入验证码，则需要额外传递captcha-id、captcha-solution两个参数
form_email、form_password是用户自己输入的登陆信息，captcha-id、captcha-solution是验证信息，其余参数在登陆中没有变化
通过观察豆瓣网站HTML可以发现，豆瓣是通过判断我们输入的验证码值(captcha-solution)与网站原有的captcha-id进行匹配对比，如果相同则允许登陆
我们可以先请求登陆网站，得到captcha-id，手动识别并输入图片验证码进行登陆
"""


# 得到captcha-id
def getCaptchaId():

    # 声明请求网页，定制请求头
    url = 'https://accounts.douban.com/login'
    headers = {'Host': 'accounts.douban.com',
               'Referer': 'https://accounts.douban.com/login',
               'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.26 Safari/537.36 Core/1.63.6788.400 QQBrowser/10.3.2767.400'}

    # 通过get请求，寻找captcha-id
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, 'lxml')
    captchaId = soup.find_all('input', type='hidden')[2].attrs['value']

    # 返回验证码图片的网址，用函数getCaptchaImage进行人工输入
    captchaImageUrl = soup.find_all('img', id='captcha_image')[0].attrs['src']

    #返回值是captchaId和验证码图片的网址
    return captchaId, captchaImageUrl

# 得到captcha-solution
def getCaptchaImage(url):

    captchaImageUrl = url
    headers = {'Host': 'www.douban.com',
               'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.10 Safari/537.36'}

    r = requests.get(captchaImageUrl, headers=headers)

    #这一步是将网页图片转为二进制，并保存为jpg格式
    with open('captcha.jpg', 'wb') as f:
        f.write(r.content)
        f.close()

    #用pillow模块包读取图片
    try:
        image = Image.open('captcha.jpg')
        image.show()

        #手动输入验证码
        captchaImage = input('Please input the captcha:')
        image.close()

    #如果没有成功打开，则需要自己去源代码文件夹寻找图片输入
    except:
        print('Please find image yourself\n')
        captchaImage = input('Please input the captcha:')
    return captchaImage


#用于进行模拟登陆
def login(userName, passWord):
    #定制登陆页面的请求头和登陆网址
    url = 'https://accounts.douban.com/login'
    headers = {'Host': 'accounts.douban.com',
               'Referer': 'https://accounts.douban.com/login',
               'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.26 Safari/537.36 Core/1.63.6788.400 QQBrowser/10.3.2767.400'}

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'lxml')

    #用try防止出现没有验证码的情况
    try:
        soup.find_all('input', type='hidden')
        captchaId = soup.find_all('input', type='hidden')[2].attrs['value']
        captchaImageUrl = soup.find_all('img', id='captcha_image')[0].attrs['src']
        captchaImage = getCaptchaImage(captchaImageUrl)

    #如果不需要填验证码则赋值为None
    except:
        captchaId = None
        captchaImage = None

    #在请求的基础上创建一个会话，该会话保持了上一次请求的cookies，利用该会话进行模拟登陆
    session = requests.session()

    #进行模拟登陆需要传递的表单
    postDict = {'form_email': userName,
                'form_password': passWord,
                'login': '登录',
                'redir': 'https://www.douban.com',
                'source': None,
                'remember': 'on'
                }

    #如果网页需要填入验证码，将其添加入传递表单
    if captchaId != None and captchaImage != None:
        postDict['captcha-id'] = captchaId
        postDict['captcha-solution'] = captchaImage

    #会话建立连接
    r = session.post(url, headers=headers, data=postDict)

    #如果连接成功(返回状态码为200)，则将这个会话作为返回值返回，否则返回None
    if str(r.status_code) == str(200):
        cookies = r.cookies.get_dict()
        with open('doubanCookies.txt', 'w')as file:
            json.dump(cookies, file)
            file.close()
        return session
    else:
        return None


def getComments(userName, passWord):

    url = 'https://movie.douban.com/subject/3168101/comments?start= %s &limit=20&sort=new_score&status=P'
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:63.0) Gecko/20100101 Firefox/63.0',
               'Host': 'movie.douban.com'}

    #使用带有cookies的session
    session = login(userName, passWord)

    if session == None:
        print("can't load session")
        return 0

    time.sleep(2)

    #采集数据
    for i in range(0, 20):
        file = open('doubanComments.txt', 'a', encoding='utf-8')
        print(i + 1, 'begin')

        page = i * 20
        url = 'https://movie.douban.com/subject/3168101/comments?start= %s &limit=20&sort=new_score&status=P' % str(
            page)
        try:
            r = session.get(url, headers=headers)
            r.encoding = 'utf-8'
            soup = BeautifulSoup(r.text, 'lxml')
            allComments = soup.find_all('span', class_='short')
            for comment in allComments:
                file.write(str(comment.string.strip()))
                file.write('\n')
            file.close()

        except:
            print(i + 1, 'end')
            file.close()
            break
        print(i + 1, 'end')
        time.sleep(2)
    print('Task ends')

if __name__ == '__main__':
    """
    userName = yourLoginName
    password = yourPassWord
    getComments(userName, password)
    
    """
