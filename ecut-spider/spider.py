import re
import requests
import urllib3

urllib3.disable_warnings()


class Spider:
    login_url = "https://cas.ecit.cn/index.jsp?service=http://portal.ecit.cn/Authentication"

    def __init__(self, url):
        self.url = url
        self.s = requests.session()

    def get_lt(self):
        r = self.s.get(self.url, verify=False)
        html = r.text
        lt = re.search(r'<div style="text-align:right;"><input type="hidden" name="lt" value="(.*?)" /></div>',
                       html).group(1)
        return lt

    def do_init(self):
        # 初始化模拟登录
        lt = self.get_lt()
        r = self.s.post(url=self.login_url, data={"username": "学号", "password": "密码",
                                                  "lt": lt, "Submit": ""}, verify=False)
        return None

    def get_ticket(self):
        # 此时已有JESSIONID 和 CASTGC 的 cookies
        r = self.s.get("http://jw.ecit.cn/", verify=False)
        pattern = re.compile(r'window.location.href="http://jw.ecit.cn/login.jsp\?ticket=(.*?)";')
        ticket = pattern.search(r.text)
        if ticket:

            return ticket.group(1)
        else:
            return "ticket 未获取"

    def do(self, ticket):
        url = "http://jw.ecit.cn/login.jsp"
        r = self.s.get(url, verify=False, params={"ticket": ticket})  # 保持登录状态
        # "http://jw.ecit.cn/gradeLnAllAction.do?type=ln&oper=qbinfo&lnxndm=2017-2018%D1%A7%C4%EA%B5%DA%D2%BB%D1%A7%C6%DA(%C1%BD%D1%A7%C6%DA)"
        # r = self.s.get("http://jw.ecit.cn/gradeLnAllAction.do", verify=False, params={
        #     "type": "ln",
        #     "oper": "qbinfo",
        #     "lnxndm": "2017-2018学年第一学期(两学期)"
        # })
        # http://jw.ecit.cn/bxqcjcxAction.do
        r = self.s.get("http://jw.ecit.cn/bxqcjcxAction.do", verify=False)
        # -----
        # http://jw.ecit.cn/xjInfoAction.do
        # r = self.s.get("http://jw.ecit.cn/xjInfoAction.do", verify=False, params={"oper": "xjxx"})
        print(r.text)


if __name__ == "__main__":
    spider = Spider(url="https://cas.ecit.cn/index.jsp?service=http://portal.ecit.cn/Authentication")
    spider.do_init()
    ticket = spider.get_ticket()
    spider.do(ticket)
    # 东华理工教务系统爬虫实例
    # 26 行的学号 密码 需要自行添加
