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


def download(url, n=0):
    try:
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/53"
                                                     "7.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36"})
    except requests.exceptions.ReadTimeout as e:
        print(e)
        if n <= 3:
            n += 1
            download(url, n)
    else:
        filename = os.path.basename(url)
        path = os.path.join('./images', filename)
        if not os.path.exists('./images'):
            os.makedirs('./images')
        try:
            with open(path, 'wb') as f:
                f.write(r.content)
        except FileNotFoundError:
            print("{}下载失败".format(filename))
        else:
            print("下载{}成功".format(filename))


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


class ThreadDownLoad(threading.Thread):
    def __init__(self, thread_name):
        threading.Thread.__init__(self)
        self.thread_name = thread_name

    def run(self):
        while True:
            if queue.empty():
                break
            download(url=BASE_URL + queue.get())


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
        print("开始线程{}".format(t.thread_name))
        t.start()

    for t in threads:
        t.join()
        print("开始线程{}".format(t.thread_name))

    print("花费时间为{}秒".format(time.time() - t0))
    ts = [ThreadDownLoad(i) for i in range(1, 11)]
    t1 = time.time()
    for t in ts:
        t.start()

    for t in ts:
        t.join()
    print("下载花费时间为{}秒".format(time.time() - t1))
    print('exit main threading')


if __name__ == '__main__':
    main()
