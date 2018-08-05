#!/usr/bin/env python

import os
import re
import threading
import time
from collections import namedtuple
from queue import Queue

import requests

"""
https://www.pixiv.net/member_illust.php?mode=medium&illust_id=69972773
"""

HEADERS = {
    'user-agent':
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.84 Safari/537.36"
}

Msg = namedtuple('Msg', ['title', 'illust_url'])
Referer = namedtuple('Referer', ['referer', 'img_url'])


class DownThread(threading.Thread):

    def __init__(self, queue, pixiv):
        threading.Thread.__init__(self)
        self.pixiv = pixiv
        self.queue = queue

    def run(self):
        while True:
            if self.queue.empty():
                break
            ref = self.queue.get()
            self.pixiv.down_url(ref.img_url, ref.referer)


class PixivSpider:
    """PixivSpider"""
    login_url = 'https://accounts.pixiv.net/login?lang=zh'
    session = requests.Session()
    req_url = 'https://www.pixiv.net/ranking.php'

    def __init__(self, username, password):
        self.username, self.password = username, password

    def _get_post_key(self) -> str:
        r = self.session.get(self.login_url, headers=HEADERS)
        key = re.search(r'<input type="hidden" name="post_key" value="(.*?)">',
                        r.text).group(1)
        return key

    def _login(self) -> None:
        key = self._get_post_key()
        r = self.session.post(
            self.login_url,
            headers=HEADERS,
            data={
                'pixiv_id': self.username,
                'captcha': '',
                'g_recaptcha_response': '',
                'password': self.password,
                'source': 'pc',
                'ref': 'wwwtop_accounts_index',
                'return_to': 'https://www.pixiv.net/',
                'post_key': key
            })
        if r.status_code == 200:
            print(f'login code: {r.status_code}')
        else:
            raise Exception('网络错误')

    def _get_tt(self) -> str:
        r = self.session.get(
            self.req_url,
            headers=HEADERS,
            params={
                'mode': 'daily',
                'content': 'illust'
            })
        tt = re.search(r'pixiv.context.token = "(.*?)";', r.text).group(1)
        return tt

    def get_html_urls(self, p: int) -> dict:
        tt = self._get_tt()
        r = self.session.get(
            self.req_url,
            params={
                'mode': 'daily',
                'content': 'illust',
                'p': p,
                'format': 'json',
                'tt': tt
            })
        return r.json()

    def get_img_url(self, page_url: str):
        r = self.session.get(page_url, headers=HEADERS)
        img_url = re.search(r'"original":"(.*?)"', r.text).group(1)
        return Referer(referer=page_url, img_url=img_url)

    def down_url(self, img_url, referer):
        url = img_url.replace('\\', '')
        print(f'dowonlad {url}')
        HEADERS['referer'] = referer
        r = self.session.get(url, headers=HEADERS)
        path = 'images'
        if not os.path.exists(f'{path}'):
            os.mkdir(path)
        with open(os.path.join(path, os.path.basename(url)), 'wb') as f:
            f.write(r.content)


def main(page: int):
    p = PixivSpider('username', 'password')
    p._login()
    d = {'contents': []}
    for i in range(1, page+1):
        d['contents'] = d['contents'] + p.get_html_urls(i)['contents']
    msgs = [
        Msg(title=j['title'],
            illust_url='https://www.pixiv.net/member_illust.php?mode=medium&illust_id=' +
            str(j['illust_id'])) for j in d['contents']
    ]
    queue = Queue()
    for msg in msgs:
        queue.put(p.get_img_url(msg.illust_url))
    tasks = [DownThread(queue, p) for i in range(1, 11)]
    t1 = time.time()
    for task in tasks:
        task.start()

    for task in tasks:
        task.join()
    print(f'total time is {time.time()-t1}')


if __name__ == "__main__":
    main(10)
