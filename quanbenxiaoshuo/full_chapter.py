from models import Category, Book, Session_class, Chapter
import os
import requests
from bs4 import BeautifulSoup
from requests import exceptions
import re


# session = Session_class()
#
#
# for book in session.query(Book).all():
#     print(book.name, os.path.join(book.href, 'xiaoshuo.html'))


def get_html(url, data={}):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0"
                             "; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36"}
    num = 1
    while num:
        try:
            r = requests.get(url, headers=headers, timeout=2, data=data)
        except TimeoutError as e:
            print(e)
            print("重新连接")
        except exceptions.ConnectionError as e:
            print(e)
            print("重新连接")
        except exceptions.ReadTimeout as e:
            print(e)
            print("重新连接")
        else:
            return r.text


def get_context(url):
    html = get_html(url)
    soup = BeautifulSoup(html, 'html.parser')
    try:
        context = eval(soup.find_all('script')[8].get_text()[10:-1])
    except IndexError as e:
        print(e)
    else:
        data = {
            'pinyin': context[3],
            'content_id': context[5],
            'sky': context[7],
            't': context[9],
        }
        url = "http://www.quanben5.com/index.php?c=book&a=ajax_content"
        while True:
            try:
                r = requests.post(url, data, timeout=2)
            except exceptions.ConnectionError as e:
                print(e)
            except exceptions.ReadTimeout as e:
                print(e)
            else:
                return r.text
    return "内容为空"


def get_chapter(html):
    soup = BeautifulSoup(html, 'html.parser')
    list = soup.find_all('li', class_="c3")
    session = Session_class()
    for i in list:
        body = get_context("http://www.quanben5.com" + i.a['href'])
        chapter = Chapter(
            href="http://www.quanben5.com" + i.a['href'],
            name=i.a.span.get_text(),
            chapter_text=body
        )
        print(i.a.span.get_text())
        session.add(chapter)
        session.commit()


def run(url):
    html = get_html(url)
    get_chapter(html)


if __name__ == '__main__':
    url = "http://www.quanben5.com/n/yishixiejun/xiaoshuo.html"
    run(url)

