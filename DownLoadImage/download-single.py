import os
import time

import requests
from queue import Queue

queue = Queue()
file = './url.txt'
BASE_URL = 'http://www.cosplayla.com'


def init():
    # 将url.txt里面的url存储到队列中
    with open(file, 'r') as f:
        for line in f:
            queue.put(line.replace('\n', ''))


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


def main():
    t0 = time.time()
    init()
    print("存储到花费队列中花费{}秒".format(time.time() - t0))
    t1 = time.time()
    while True:
        if queue.empty():
            break
        url = BASE_URL + queue.get()
        download(url)
    print("共用{}秒".format(time.time() - t1))
    # 21:01 --> 21:36
    # 花费35分钟下载4239张图片


if __name__ == '__main__':
    main()
