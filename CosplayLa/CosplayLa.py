from .Support import *
from bs4 import BeautifulSoup
import re
import os


def parser(content):
    soup = BeautifulSoup(content, 'html.parser')
    items = soup.find_all('li', attrs={'class': 'font12 fleft'})
    ret = []

    for item in items:
        ret.append("http://cosplay.la/" + item.a.attrs['href'])

    return ret  # 图集的地址列表


def parser2(content):
    soup = BeautifulSoup(content, 'html.parser')
    div = soup.find_all('div', attrs={'class': 'talk_pic hauto'})[0]
    ret = []

    for item in div.find_all('p', attrs={'class': 'mbottom10'}):
        ret.append(item.a.img.attrs['src'])
    return ret  # 图片地址的列表


def getPageList(content):
    soup = BeautifulSoup(content, 'html.parser')
    div = soup.find_all('div', attrs={'class': 'pagen tcenter mbottom20 font16'})[0]
    page = div.find_all('a')[-2].get_text()
    pageList = []

    for i in range(int(page) + 1):
        pageList.append("http://cosplay.la/photo/index/0-0-{}".format(i))

    return pageList  # 所有页面的列表


def getName(url):
    name = re.findall(r'http://img.cosplay.la//(.*?)\?imageView.*?', url)[0]
    return name


def main():
    root_url = "http://cosplay.la/photo"

    html = DownloadPage(root_url)

    pages = getPageList(html)
    for url in pages[:10]:  # 前十页
        html = DownloadPage(url)
        page_list = parser(html)

        for page in page_list:  # 一页20条
            html = DownloadPage(page)

            for img in parser2(html):  # 一条多个图片
                try:
                    filepath = os.path.join(os.getcwd(), 'images', getName(img))
                    DownloadFile(img, filepath)
                except OSError as e:
                    print(e)


if __name__ == "__main__":
    main()
