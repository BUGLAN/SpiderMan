
"""
* 爬取全本小说网全站小说
* 按类别分类
* 爬取入库
* requests
* beautifulsoup4
* sqlalchemy
发现站点地图的书籍不全仅有1000条,现改为使用根地址为
url = "http://www.quanben5.com/category/1.html"
"""

from requests import exceptions
import requests
from bs4 import BeautifulSoup
import re
from models import Book, Session_class, Category
import datetime
import socket
from urllib3.exceptions import ReadTimeoutError


def get_html(url):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0"
                             "; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36"}
    num = 5
    while num > 0:
        try:
            r = requests.get(url, headers=headers, timeout=2)
        except socket.timeout as e:
            print("错误 {}".format(e))
            print("正在重新连接")
            continue
        except exceptions.ConnectionError as e:
            print("错误 {}".format(e))
            print("正在重新连接")
            continue
        except ReadTimeoutError as e:
            print("错误 {}".format(e))
            print("正在重新连接")
            continue
        except exceptions.ReadTimeout as e:
            print("错误 {}".format(e))
            print("正在重新连接")
            continue
        else:
            return r.text
    else:
        print("连接错误--超时连接3次")


def get_categories(html):
    soup = BeautifulSoup(html, 'html.parser')
    categories = soup.find_all('li')
    session = Session_class()
    for category in categories:
        cat = Category(
            name=category.get_text(),
            created_time=datetime.datetime.now(),
        )
        session.add(cat)
    session.commit()
    return session.query(Category).all()


def get_pages(html):
    max_page = re.findall(r'<span class="cur_page">1 / (.*?)</span>', html)
    return max_page


def get_urls(html, category):
    try:
        max_page = get_pages(html)[0]
    except IndexError as e:
        print(e)
    else:
        urls = []
        for url in range(1, int(max_page) + 1):
            urls.append("http://www.quanben5.com/category/{}_{}.html".format(category, url))
        return urls


def get_book(html, category_id):
    soup = BeautifulSoup(html, 'html.parser')
    books = soup.find_all('h3')
    # 爬取此页的书名和链接
    session = Session_class()
    for book in books:
        rebook = Book(
            name=book.get_text(),
            href=book.find('a')['href'],
            created_time=datetime.datetime.now(),
            category_id=category_id
        )
        print("保存--<<{}>>--{}".format(book.get_text(), datetime.datetime.now()))
        session.add(rebook)
    session.commit()
    # 保存书名和链接


def run():
    root_url = "http://www.quanben5.com/category/1.html"
    root_html = get_html(root_url)
    category_list = get_categories(root_html)
    for category_obj in category_list:
        try:
            for url in get_urls(get_html("http://www.quanben5.com/category/{}.html".format(category_obj.id)), category_obj.id):
                html = get_html(url)
                get_book(html, category_obj.id)
        except IndexError as e:
            print(e)
            print("类别{}  无书籍".format(category_obj.name))
        except TypeError as e:
            print(e)
            print("类别{}  无书籍".format(category_obj.name))


if __name__ == '__main__':
    run()


