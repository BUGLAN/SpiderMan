import re
import sys
from queue import Queue
import aiohttp
import asyncio
import aiofiles
import os
import time

headers = {
    "user-agent":
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.3 \
        6 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36"
}
"""
先异步, 再改成多线程
使用 queue 就无需使用锁
封装下载模块
写大点就需要使用代理
"""

url_queue = Queue()


class Pixiv:
    get_key_url = "https://accounts.pixiv.net/login?lang=zh&source=\
            pc&view_type=page&ref=wwwtop_accounts_index"

    request_url = "https://www.pixiv.net/ranking.php?mode=male"
    login_url = "https://accounts.pixiv.net/api/login?lang=zh"

    def __init__(self, username, password, session):
        self.username = username
        self.password = password
        self.session = session

    async def _get_key(self):
        async with self.session.get(self.get_key_url) as r:
            key = re.search(
                r'<input type="hidden" name="post_key" value="(.*?)">', await
                r.text()).group(1)
        return key

    async def _login(self):
        key = await self._get_key()
        async with self.session.post(
                self.login_url,
                data={
                    "pixiv_id": self.username,
                    "captcha": "",
                    "g_recaptcha_response": "",
                    "source": "pc",
                    "password": self.password,
                    "ref": "wwwtop_accounts_index",
                    "return_to": "https://www.pixiv.net/",
                    "post_key": key
                }) as r:
            if r.status == 200:
                print("login success {}".format(r.status))
            else:
                print("login fail {}".format(r.status))
                sys.exit()

    async def _get_tt(self):
        async with self.session.get(
                "https://www.pixiv.net/ranking.php?mode=male") as r:
            tt = re.search('pixiv.context.token = "(.*?)";', await
                           r.text()).group(1)
            return tt

    async def get_urls(self, tt, p):
        async with self.session.get(
                self.request_url,
                params={
                    "mode": "male",
                    "p": p,
                    "format": "json",
                    "tt": tt
                }) as r:
            result = re.findall(r'\'illust_id\': (.*?),', str(await r.json()))
            return result

    """
    async def parser_json(self, json, result):
        await asyncio.sleep(0)
        async for content in json['contents']:
            result.append(content['illust_id'])
    """

    async def _get_manga_urls(self, id):
        async with self.session.get(
                "https://www.pixiv.net/member_illust.php?mode=manga&illust_id="
                + str(id)) as r:

            urls = re.findall(r'data-src="(.*?)" data-index="\d+"', await
                              r.text())
        return urls

    async def get_master_img(self, id):
        async with self.session.get(
                "https://www.pixiv.net/member_illust.php?mode=medium&illust_id="
                + str(id)) as r:
            origin = re.search(r'data-src="(.*?)" class="original-image">',
                               await r.text())
        try:
            url = origin.group(1)
        except AttributeError as e:
            urls = await self._get_manga_urls(id)
            return urls, "https://www.pixiv.net/member_illust.php?mode=medium&illust_id=" + str(id)
            pass
        else:
            return url, "https://www.pixiv.net/member_illust.php?mode=medium&illust_id=" + str(id)

    async def down_binary(self, url, referer):
        print(referer)
        headers['referer'] = referer
        try:
            async with self.session.get(url, headers=headers) as r:
                return await r.content.read()
        except aiohttp.ServerDisconnectedError as e:
            print(e)
            pass

    async def save_file(self, binary, path):
        async with aiofiles.open(path, 'wb') as f:
            await f.write(binary)

    async def down(self, result):
        binary = await self.down_binary(result[0], result[1])
        await self.save_file(
            binary, os.path.join(".", "image", os.path.basename(result[0])))

    async def run(self, loop):
        await self._login()
        # 首先所有id前十页
        tt = await self._get_tt()
        ids_tasks = [
            loop.create_task(self.get_urls(tt, i)) for i in range(1, 11)
        ]
        finshed, unfinished = await asyncio.wait(ids_tasks)
        all_result = [r.result() for r in finshed]
        print("start")
        results = []
        for i in all_result:
            results += i
        tasks = [loop.create_task(self.get_master_img(id)) for id in results]
        finished, unfinished = await asyncio.wait(tasks)
        all_result = [r.result() for r in finished]
        if not os.path.exists("./image"):
            os.makedirs("./image")
        results = []
        for result in all_result:
            if isinstance(result[0], str):
                results.append((result[0], result[1]))
            elif isinstance(result[0], list):
                for url in result[0]:
                    results.append((url, result[1]))
        tasks = [loop.create_task(self.down(result)) for result in results]
        finished, unfinished = await asyncio.wait(tasks)
        all_result = [r.result() for r in finished]
        """
        for id in ids:
            if isinstance(self.get_master_img(id), str):
                urls.append(self.get_master_img)
            else:
                urls += self.get_master_img(id)
        print(urls)
        print("end")
        """


async def main(loop):
    async with aiohttp.ClientSession(headers=headers) as session:
        pixiv = Pixiv("username", "password", session)
        await pixiv.run(loop)


if __name__ == "__main__":
    t1 = time.time()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(loop))
    print("total time is {}".format(time.time() - t1))
