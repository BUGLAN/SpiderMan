import requests


def DownloadPage(url, **kwargs):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/53"
                      "7.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36"
    }
    while True:
        try:
            r = requests.get(url, headers=headers, timeout=3)
            r.raise_for_status()
        except:
            print("Link Error")
        else:
            r.encoding = r.apparent_encoding
            return r.text


def DownloadFile(url, filepath, **kwargs):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/53"
                      "7.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36"
    }
    num = 2
    while num > 0:
        try:
            r = requests.get(url, headers=headers, timeout=10)
            r.raise_for_status()
        except:
            print(url + "Download Fail")
            num = num - 1
        else:
            with open(filepath, "wb") as f:
                f.write(r.content)
            return True
