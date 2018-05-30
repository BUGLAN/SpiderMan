import requests
from bs4 import BeautifulSoup
from requests import exceptions
import re


def get_html(url):
    cookie = "__cfduid=d042eb1ccc0b85afb418728c8277f2e691509249772; _ga=GA1.2.1706585417.1509249774"
    headers = {
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "Cookie": cookie,
        "Host": "api.jandan.net",
        "Pragma": "no-cache",
        "Referer": "http://jandan.net/ooxx",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/53"
                      "7.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36"
    }

    date = {"post_id": "l", "rate_score": "o"}

    while True:
        try:
            r = requests.post(url, headers=headers, params=date)
        except exceptions.ReadTimeout as e:
            print("exceptions.ReadTimeout  {}".format(e))
        except TimeoutError as e:
            print("TimeoutError  {}".format(e))
        except exceptions.ConnectionError as e:
            print("exceptions.ConnectionError  {}".format(e))
        else:
            return r.text


def get_page(html):
    soup = BeautifulSoup(html, 'html.parser')
    page = soup.find('span', class_="current-comment-page").get_text()[1: -1]
    return page


def get_img(html):
    imgs = re.findall(r'<a href="(.*?)" target="_blank" class="view_img_link">[查看原图]</a>', html)
    print(imgs)


def run():
    url = "http://jandan-rate.php"
    html = get_html(url)
    print(html)
    get_img(html)


if __name__ == '__main__':
    run()

"""
 eval(function(p,a,c,k,e,r){e=function(c){return c.toString(a)};if(!''.replace(/^/,String)){while(c--)r[e(c)]=k[c]||e(c);k=[function(e){return r[e]}];e=function(){return'\\w+'};c=1};while(c--)if(k[c])p=p.replace(new RegExp('\\b'+e(c)+'\\b','g'),k[c]);return p}('(g(){1 d=["j","a","0","d","a","0",".","0","e","f"];1 3=7 8(d.2(\'\')+\'$\');4(!3.9(b.c)){1 a=5.6.h;4(a==\'/\'){a=\'\'}5.6.i=\'k://\'+d.2(\'\')+\'/\'+a}})($l);',22,22,'n|var|join|r|if|window|location|new|RegExp|test||document|domain|||t|function|pathname|href||http|JANDAN'.split('|'),0,{}));
    ajax({type:"POST",dataType:"json",url:"/jandan-rate.php",data:{post_id:l,rate_score:o}
"""