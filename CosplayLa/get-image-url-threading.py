import os
import re
import time
import threading

import requests
from queue import Queue

queue = Queue()
url = "http://www.cosplayla.com/picture-4/?page="
BASE_URL = "http://www.cosplayla.com"


def parser_page(url):
    # url = "http://www.cosplayla.com/picture-4/?page=1"
    html = DownLoad().download_page(url)
    need_handle_url = re.findall(r'<li class="t"><a href="(.*?)" target="_blank">', html)
    return need_handle_url


def parser_html(url):
    url = BASE_URL + url
    context = DownLoad().download_page(url)
    pics = re.findall('<img src="(.*?)" width="750" />', context)
    pics = list(set(pics))
    for pic in pics:
        queue.put(pic)


class ThreadUrl(threading.Thread):
    def __init__(self, thread_name, i):
        threading.Thread.__init__(self)
        self.thread_name = thread_name
        self.i = i

    def run(self):
        global url
        urls = parser_page(url + str(self.i))
        for url in urls:
            parser_html(url)


class DownLoad:
    def __init__(self):
        self._headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/53"
                                       "7.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36"}
        self._timeout = 10

    def download_page(self, url):
        # n = 5
        # while n > 0:
        #     try:
        #         r = requests.get(url, headers=self._headers, timeout=self._timeout)
        #     except requests.exceptions.ReadTimeout:
        #         n -= 1
        #     else:
        #         r.encoding = r.apparent_encoding
        #         return r.text
        """
        注意 ‘r.encoding = r.apparent_encoding’
        这行操作是cpu密集型
        多线程下会减慢速度
        在这个程序中如果不加的话所需时间为12.5秒左右
        加了的话 为36秒
        """
        try:
            r = requests.get(url, headers=self._headers, timeout=self._timeout)
        except requests.exceptions.ReadTimeout as e:
            print(e)
            return self.download_page(url)
        else:
            return r.text


def main():
    t0 = time.time()
    threads = [ThreadUrl(i, i) for i in range(1, 11)]
    for t in threads:
        print(t.thread_name)
        t.start()

    for t in threads:
        t.join()
    urls = []
    while True:
        if queue.empty():
            break
        urls.append(queue.get())
    print(urls)
    print("花费时间为{}， 爬取了{}张图片".format(time.time() - t0, len(urls)))
    print('exit main threading')


if __name__ == '__main__':
    main()
