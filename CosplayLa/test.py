from .CosplayLa import *
import os 


url = "http://cosplay.la/photo/show/8028"
html = DownloadPage(url)
urls = parser2(html)
for url in urls:
    print(url)
