import re
import time

from Support import *

URL = "http://www.cosplayla.com/picture-4/"
BASE_URL = "http://www.cosplayla.com"
pic_urls = []


def parser_page(url):
    # url = "http://www.cosplayla.com/picture-4/?page=1"
    html = DownloadPage(url)
    need_handle_url = re.findall(r'<li class="t"><a href="(.*?)" target="_blank">', html)
    for url in need_handle_url:
        parser_html(url)

    # return None


def parser_html(url):
    url = BASE_URL + url
    html = DownloadPage(url)
    pics = re.findall(r'<img src="(.*?)" width="750" />', html)
    global pic_urls
    pics = list(set(pics))
    pic_urls += pics

    # return None


def main():
    url = "http://www.cosplayla.com/picture-4/?page="
    for n in range(1, 11):
        parser_page(url + str(n))


if __name__ == '__main__':
    t0 = time.time()
    main()
    print(pic_urls)
    print("花费了{}时间, 得到了{}个图像".format(time.time() - t0, len(pic_urls)))
