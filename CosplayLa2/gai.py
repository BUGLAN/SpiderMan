import re
import os
import requests
import threading

from queue import Queue


class ThreadCrawlHtml(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        # 爬取html
        pass


class ThreadUrlCrawl(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        # 由页面爬取url
        pass


class ThreadDownLoad(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        # 下载线程
        pass


def main():
    pass


if __name__ == '__main__':
    main()
