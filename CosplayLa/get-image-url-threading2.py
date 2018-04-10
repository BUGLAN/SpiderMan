import threading
from queue import Queue
import requests
import re
import time

URL = []


class ThreadHtml(threading.Thread):
    def __init__(self, thread_id, page):
        threading.Thread.__init__(self)
        self.thread_id = thread_id
        self.page = page
        self.queue = None

    def run(self):
        # 这个程序爬取url并将其存到队列里面
        # 抓取每一页的url
        cosplayla = CosplayLa()
        cosplayla.get_urls(page=self.page)
        while True:
            try:
                cosplayla.parser()
            except IndexError:
                break
        self.queue = cosplayla.queue
        print('end {}'.format(self.thread_id))


class CosplayLa:
    def __init__(self, ):
        self._root_url = 'http://www.cosplayla.com/picture-4/'
        self.urls = []
        self.download = DownLoad()
        self.queue = Queue()

    def get_urls(self, page):
        context = self.download.download_page(self._root_url, {"page": page})
        urls = re.findall('<div class="pic"><a href="(.*?)" target="_blank">', context)
        self.urls = urls
        return urls

    def parser(self):
        url = 'http://www.cosplayla.com' + self.urls.pop()
        context = requests.get(url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/53"
                          "7.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36"
        }).text
        urls = re.findall('<img src="(.*?)" width="750" />', context)
        for url in urls:
            if url == '/picup/':
                urls.remove(url)
            else:
                self.queue.put(url)
        global URL
        URL += urls
        return self.queue

    def start(self):
        t0 = time.time()
        threads = [ThreadHtml(thread_id=i, page=i) for i in range(1, 11)]
        for t in threads:
            print("start {}".format(t.thread_id))
            t.start()
        for t in threads:
            t.join()
        url = list(set(URL))
        print(url)
        print("花费时间{}, 共{}条url".format(time.time() - t0, len(url)))

        # 开启10个线程


class DownLoad:
    def __init__(self):
        self._headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/53"
                                       "7.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36"}
        self._timeout = 10

    def download_page(self, url, page):
        n = 5
        while n > 0:
            try:
                r = requests.get(url, params=page, headers=self._headers, timeout=self._timeout)
            except requests.exceptions.ReadTimeout:
                n -= 1
            else:
                # r.encoding = r.apparent_encoding
                return r.text


if __name__ == '__main__':
    cosplayla = CosplayLa()
    cosplayla.start()
