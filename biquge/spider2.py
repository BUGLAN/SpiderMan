import re
import os

from download import *


class Novel:
    search_url = "http://www.biquge5200.com/modules/article/search.php"

    def search(self, keyword):
        # biquge 搜索功能
        page = DownLoad.download_page(self.search_url, params={"searchkey": keyword}, timeout=1.5)
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


class Book:
    """
    @:param url: 书籍详情页 如 http://www.biquge5200.com/85_85278/
    """
    chapters = []
    introduce = None

    def __init__(self, url):
        self.url = url

    def get_chapters_and_introduce(self):
        # 获取章节目录和介绍
        html = DownLoad.download_page(self.url)
        pattern = re.compile('<div id="intro">.*?<p>(.*?)</p>.*?</div>', re.S)
        introduce = "<p>" + pattern.findall(html)[0] + "</p>"

        pattern = re.compile('<dd><a href="(.*?)">(.*?)</a></dd>')
        chapters = pattern.findall(html)
        self.chapters = chapters
        self.introduce = introduce
        return self.chapters, self.introduce

    def previous_and_next_chapters(self, kurl):
        if not self.chapters:
            Book.get_chapters(self)
        k_index = None
        for url, title in self.chapters:
            if kurl == url:
                k_index = self.chapters.index((url, title))
        if k_index == 0:
            return (os.path.dirname(self.chapters[k_index][0]), '目录'), self.chapters[k_index + 1]
        elif k_index == len(self.chapters) - 1:
            return self.chapters[k_index - 1], (os.path.dirname(self.chapters[k_index][0]), '书籍目录')
        return self.chapters[k_index - 1], self.chapters[k_index + 1]

    @staticmethod
    def get_page(page_url):
        html = DownLoad.download_page(page_url)
        try:
            content = re.compile('<div id="content">　　(.*?)</div>', re.S).findall(html)[0]
        except IndexError as e:
            # content = re.compile('<div id="content">    (.*?)</div>', re.S).findall(html)
            # if content:
            #     print(content)
            #     return content[0]
            return "%s 未获取到内容请联系管理员" % e
        return content


if __name__ == '__main__':
    book = Book("http://www.biquge5200.com/85_85278/")
    print(book.get_chapters_and_introduce())
    print(book.previous_and_next_chapters("http://www.biquge5200.com/85_85278/153057121.html"))
