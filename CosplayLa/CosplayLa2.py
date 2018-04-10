import logging
import threading
from queue import Queue
import requests
import re
import os


def get_logger():
    logger = logging.getLogger("CosplayLa2")
    logger.setLevel(logging.DEBUG)
    handler = logging.FileHandler('CosplayLa2.log', encoding='utf8')
    formatter = logging.Formatter('%(asctime)s - %(threadName)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


class ThreadHtml(threading.Thread):
    def __init__(self, thread_id, logger, page, ):
        threading.Thread.__init__(self)
        self.thread_id = thread_id
        self.logger = logger
        self.page = page
        self.queue = None

    def run(self):
        # 这个程序爬取url并将其存到队列里面
        # 抓取每一页的url
        cosplayla = CosplayLa(logger=self.logger)
        cosplayla.get_urls(page=self.page)
        while True:
            try:
                cosplayla.parser()
            except IndexError as e:
                logger.error("列表为空: {}".format(e))
                break
        self.queue = cosplayla.queue
        print('end {}'.format(self.thread_id))
        logger.info('end {}'.format(self.thread_id))


class ThreadUrl(threading.Thread):
    def __init__(self, thread_id, logger, queue):
        threading.Thread.__init__(self)
        self.thread_id = thread_id
        self.logger = logger
        self.queue = queue

    def run(self):
        cosplayla = CosplayLa(logger=self.logger)
        while True:
            try:
                cosplayla.down(self.queue)
            except IndexError as e:
                logger.error("队列为空 {}".format(e))
                break
        print("下载完成")


class CosplayLa:
    def __init__(self, logger):
        self._root_url = 'http://www.cosplayla.com/picture-4/'
        self.logger = logger
        self.urls = []
        self.download = DownLoad(logger)
        self.queue = Queue()

    def get_urls(self, page):
        context = self.download.download_page(self._root_url, {"page": page})
        urls = re.findall('<div class="pic"><a href="(.*?)" target="_blank">', context)
        self.urls = urls
        return urls

    def parser(self):
        url = 'http://www.cosplayla.com' + self.urls.pop()
        content = requests.get(url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/53"
                          "7.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36"
        }).text
        urls = re.findall('<img src="(.*?)" width="750" />', content)
        for url in urls:
            if url == '/picup/':
                urls.remove(url)
            else:
                self.queue.put(url)
                self.logger.info("爬取了 {}".format(url))
        return self.queue

    def down(self, queue):
        url = queue.get()
        self.download.download_file('http://www.cosplayla.com' + url)
        self.logger.info('下载{filename}成功'.format(filename=url.split('/')[-1]))

    def start(self):
        threads = [ThreadHtml(thread_id=i, logger=self.logger, page=i) for i in range(1, 11)]
        for t in threads:
            print("start {}".format(t.thread_id))
            t.start()
        for t in threads:
            t.join()

        queues = [t.queue for t in threads]

        # 开启10个线程
        ts = [ThreadUrl(thread_id="queue" + str(n), logger=self.logger, queue=queue)
              for n, queue in enumerate(queues)]

        for t in ts:
            t.start()

        for t in ts:
            t.join()

        logger.info("MainThread exit")


class DownLoad:
    def __init__(self, logger):
        self._headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/53"
                                       "7.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36"}
        self._timeout = 10
        self.logger = logger

    def download_page(self, url, page):
        n = 5
        while n > 0:
            try:
                r = requests.get(url, params=page, headers=self._headers, timeout=self._timeout)
            except requests.exceptions.ReadTimeout as e:
                logger.error("在下载{url}时出现错误: (e)".format(url=url, e=e))
                n -= 1
            else:
                # r.encoding = r.apparent_encoding
                return r.text

    def download_file(self, url):
        n = 5
        while n > 0:
            try:
                r = requests.get(url, headers=self._headers, timeout=self._timeout)
            except requests.exceptions.ReadTimeout as e:
                logger.error("在下载{url}时出现错误: (e)".format(url=url, e=e))
                n -= 1
            else:
                # r.encoding = r.apparent_encoding
                path = os.path.join(os.getcwd(), 'images')
                if not os.path.exists(path):
                    logger.info("目录不存在，创建目录{}".format(path))
                    os.makedirs(path)
                filename = url.split('/')[-1]
                with open(os.path.join(path, filename), 'wb') as f:
                    f.write(r.content)
                logger.info("文件{}下载成功".format(filename))
                break


if __name__ == '__main__':
    logger = get_logger()
    cosplayla = CosplayLa(logger)
    cosplayla.start()
