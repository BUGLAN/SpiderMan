import re
from download import *


class Spider:

    def __init__(self):
        self.search_url = "http://www.biquge5200.com/modules/article/search.php"

    @staticmethod
    def search(keyword):
        """
        搜索笔趣阁关键字前50条
        # http://www.biquge5200.com/modules/article/search.php?searchkey=keyword
        # get method
        """
        page = DownLoad.download_page("http://www.biquge5200.com/modules/article/search.php",
                                      params={"searchkey": keyword}, timeout=1.5)
        book_message = re.compile('<td class="odd"><a href="(.*?)">(.*?)</a></td>.*?'
                                  '<td class="even"><a href="(.*?)" target="_blank"> (.*?)</a></td>.*?'
                                  '<td class="odd">(.*?)</td>.*?'
                                  '<td class="even">(.*?)</td>.*?'
                                  '<td class="odd" align="center">(.*?)</td>.*?'
                                  '<td class="even" align="center">(.*?)</td>', re.S)
        # 使用正则匹配相应字符串 re.DOTALL / re.S 使'.' 匹配任意字符，包括换行符
        items = book_message.findall(page)
        if items:
            # 异常处理
            for item in items:
                print(item)
            return items
        print("无搜索结果")
        return "无搜索结果"

    @staticmethod
    def get_lists(url):
        html = DownLoad.download_page(url)
        pattern = re.compile('<div id="intro">.*?<p>(.*?)</p>.*?</div>', re.S)
        intro = "<p>" + pattern.findall(html)[0] + "</p>"
        # 获取简介
        pattern = re.compile('<dd><a href="(.*?)">(.*?)</a></dd>')
        chapters = pattern.findall(html)
        # for chapter in chapters:
        #     print(chapter)
        return chapters, intro

    @staticmethod
    def get_page(url):
        # http://www.biquge5200.com/85_85278/150792869.html
        html = DownLoad.download_page(url)
        try:
            content = re.compile('<div id="content">　　(.*?)</div>', re.S).findall(html)[0]
        except IndexError as e:
            # content = re.compile('<div id="content">    (.*?)</div>', re.S).findall(html)
            # if content:
            #     print(content)
            #     return content[0]
            return "%s 未获取到内容请联系管理员" % e
        return content
