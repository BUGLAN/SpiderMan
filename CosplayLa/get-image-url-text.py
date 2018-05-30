import re
import time
import threading

from Support import *

pic_urls = []
url = "http://www.cosplayla.com/picture-4/?page="
BASE_URL = "http://www.cosplayla.com"


def parser_page(url):
    # url = "http://www.cosplayla.com/picture-4/?page=1"
    html = DownloadPage(url)
    need_handle_url = re.findall(r'<li class="t"><a href="(.*?)" target="_blank">', html)
    for url in need_handle_url:
        parser_html(url)


def parser_html(url):
    url = BASE_URL + url
    html = DownloadPage(url)
    pics = re.findall(r'<img src="(.*?)" width="750" />', html)
    global pic_urls
    pics = list(set(pics))
    pic_urls += pics


class ThreadUrl(threading.Thread):
    def __init__(self, thread_name, i):
        threading.Thread.__init__(self)
        self.thread_name = thread_name
        self.i = i

    def run(self):
        parser_page(url + str(self.i))


def main():
    t0 = time.time()
    threads = [ThreadUrl(i, i) for i in range(1, 11)]
    for t in threads:
        t.start()

    for t in threads:
        t.join()
    print(pic_urls)
    print("花费时间为{}， 爬取了{}张图片".format(time.time() - t0, len(pic_urls)))


if __name__ == '__main__':
    main()