import re
import os
import time
from concurrent import futures

import requests

headers = {
    "User-Agent":
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Appl"
    "eWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36"
}


class PixivSpider:
    base_url = "https://accounts.pixiv.net/login?lang=zh&source=pc&view_type=page&ref=wwwtop_accounts_index"
    login_url = "https://accounts.pixiv.net/api/login"
    # headers = headers
    data = {
        "lang": "zh",
        "pixiv_id": "",
        "captcha": "",
        "g_recaptcha_response": "",
        "password": "",
        "post_key": "",
        "source": "pc",
        "ref": "wwwtop_accounts_index",
        "return_to": "https://www.pixiv.net/"
    }

    def __init__(self, username, password):
        self.data['pixiv_id'] = username
        self.data['password'] = password
        self.images = []
        self.d = DownLoad()

    def _get_id(self):
        r = self.d.down_html(self.base_url)
        key = re.search(r'<input type="hidden" name="post_key" value="(.*?)">',
                        r.text).group(1)
        return key

    def login_in(self):
        self.data['post_key'] = self._get_id()
        r = self.d.post_to(self.login_url, data=self.data)
        print("登陆状态 %s %s" % (r.status_code, 'OK'
                              if r and r.status_code == 200 else ''))

    def _get_tt(self):
        r = self.d.down_html("https://www.pixiv.net/ranking.php?mode=daily")
        tt = re.search(r'pixiv.context.token = "(.*?)";', r.text).group(1)
        return tt

    def get_urls(self, p=1):
        # 获取图片的具体url
        url = "https://www.pixiv.net/ranking.php"
        params = {"mode": "daily", "p": p, "format": "json", "tt": ""}
        tt = self._get_tt()
        params['tt'] = tt
        r = self.d.down_html(url, params=params)
        urls = []
        for item in r.json()['contents']:
            urls.append(
                "https://www.pixiv.net/member_illust.php?mode=medium&illust_id="
                + str(item['illust_id']))
        return urls

    def _get_manga(self, url):
        r = self.d.down_html(url)
        images = re.findall(r'data-src="(.*?)" data-index="\d+">', r.text)
        return images

    def get_image(self, url):
        r = self.d.down_html(url)
        manga = re.search(r'查看更多', r.text)
        if manga:
            url = url.replace('medium', 'manga')
            images = self._get_manga(url)
            name = re.search(r'<h1 class="title">(.*?)</h1>', r.text).group(1)
            return images, name
        else:
            image = re.search(
                r'<img alt="(.*?)" width="\d+" height="\d+" data-src="(.*?)" class="original-image">',
                r.text)
        return image.group(2), image.group(1)

    def down_image(self, referer, url, filename=None, path='./images'):
        if filename:
            filename += '.' + url.split('.')[-1]
            if filename in self.images:
                filename = os.path.basename(url)
        else:
            filename = os.path.basename(url)
        if '\\' in path:
            path.replace('\\', '-')
        if not os.path.exists(path):
            os.mkdir(path)
        headers['referer'] = referer
        r = self.d.down_html(url, headers=headers)
        with open(os.path.join(path, filename), 'wb') as f:
            f.write(r.content)
        self.images.append(filename)
        print("图片 {} 下载成功".format(filename))


class DownLoad:
    def __init__(self):
        self.s = requests.Session()

    def down_html(self, url, n=0, **kwargs):
        try:
            r = self.s.get(url, **kwargs)
        except requests.exceptions.ReadTimeout:
            if n < 5:
                n += 1
                self.down_html(url, n, **kwargs)
        except requests.exceptions.ConnectionError:
            if n < 5:
                n += 1
                self.down_html(url, n, **kwargs)
        else:
            return r

    def post_to(self, url, n=0, **kwargs):
        try:
            r = self.s.post(url, **kwargs)
        except requests.exceptions.ReadTimeout:
            if n < 3:
                n += 1
                self.post_to(url, n, **kwargs)
            return False
        else:
            return r

    def down_file(self, url, n=0):
        pass


"""
https://www.pixiv.net/ranking.php?mode=daily&p=2&format=json&tt=48e651f09109dd281bd47fc30edec4f3
"""


def handle_exc(spider, url):
    if spider.get_image(url):
        image_url, image_name = spider.get_image(url)
        try:
            spider.down_image(url, image_url, image_name)
        except OSError:
            print("文件名不可用, 更换文件名")
            spider.down_image(url, image_url)
        except requests.exceptions.ConnectionError as e:
            print(e)
            spider.down_image(url, image_url, image_name)
        except AttributeError:
            for i, u in enumerate(image_url):
                spider.down_image(
                    url,
                    u,
                    filename=image_name + '-' + str(i),
                    path='./images/{filename}'.format(filename=image_name))


def main(p=1):
    urls = spider.get_urls(p)
    for url in urls:
        try:
            handle_exc(spider, url)
        except Exception as e:
            print('{e} {url} 下载失败'.format(e=e, url=url))
            f.write(url + '\n')


if __name__ == '__main__':
    f = open('error.txt', 'a')
    t0 = time.time()
    spider = PixivSpider(username='buglan', password='ls52674364')
    spider.login_in()
    with futures.ThreadPoolExecutor(max_workers=20) as executor:
        executor.map(main, range(1, 11))
    print("total is {}".format(time.time() - t0))
    f.close()
