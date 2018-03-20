from .download import DownLoad


class Search:
    # biquge 搜索类 获得其章节列表 作者 分类 连载 更新时间
    search_url = "http://www.biquge5200.com/modules/article/search.php"

    def __init__(self, keyword):
        page = DownLoad.download_page(self.search_url, params={"keyword": keyword})
        pass
