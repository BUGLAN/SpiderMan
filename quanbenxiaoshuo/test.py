import requests
from bs4 import BeautifulSoup
import json


url = "http://www.quanben5.com/n/yishixiejun/7524.html"
r = requests.get(url)
soup = BeautifulSoup(r.text, 'html.parser')
context = eval(soup.find_all('script')[8].get_text()[10:-1])
for i in context:
    print(i)
data = {
    'pinyin': context[3],
    'content_id': context[5],
    'sky': context[7],
     't': context[9],
}

url = "http://www.quanben5.com/index.php?c=book&a=ajax_content"
r = requests.post(url, data)
print(r.text)


"""
function ajax_post(){
	var c = arguments[0] ? arguments[0] : '';
	var a = arguments[1] ? arguments[1] : '';
	for (var i=2;i<arguments.length;i=i+2){
		var field_name=arguments[i] ? arguments[i] : '';
		var field_value=arguments[i+1] ? arguments[i+1] : '';
		ajax.setVar(field_name,field_value);
	}
	ajax.setVar('_type','ajax');
	ajax.requestFile =_cms+'/index.php?c='+c+'&a='+a;
	ajax.method='POST';
	ajax.onCompletion = whenCompleted;
	ajax.onError = whenError;
	ajax.runAJAX();
}
"""
