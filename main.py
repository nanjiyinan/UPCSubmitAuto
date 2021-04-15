import os
import requests
import json
import lxml.html
import re

signIn = {'username': os.environ["USERNAME"], #学号
          'password': os.environ["PASSWORD"]} #登陆密码

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36',
}

conn = requests.Session()
signInResponse= conn.post(
    url="https://app.upc.edu.cn/uc/wap/login/check",
    headers=headers,
    data= signIn, 
    timeout=10
)

historyResponse = conn.get(
    url="https://app.upc.edu.cn/ncov/wap/default/index?from=history",
    headers=headers,
    data={'from': 'history'},
    timeout=10
)
historyResponse.encoding = "UTF-8"

html = lxml.html.fromstring(historyResponse.text)
JS = html.xpath('/html/body/script[@type="text/javascript"]')
JStr = JS[0].text
default = re.search('var def = {.*};',JStr).group()
oldInfo = re.search('oldInfo: {.*},',JStr).group()

firstParam = re.search('sfzgsxsx: .,',JStr).group()
firstParam = '"' + firstParam.replace(':','":')
secondParam = re.search('sfzhbsxsx: .,',JStr).group()
secondParam = '"' +  secondParam.replace(':','":')
lastParam = re.search('szgjcs: \'(.*)\'',JStr).group()
lastParam = lastParam.replace('szgjcs: \'','').rstrip('\'')

newInfo = oldInfo
newInfo = newInfo.replace('oldInfo: {','{' + firstParam + secondParam).rstrip(',')

defaultStrip = default.replace('var def = ','').rstrip(';')
defdic = json.loads(defaultStrip)

dic = json.loads(newInfo)
dic['ismoved'] = '0'
for j in ["date","created","id","gwszdd","sfyqjzgc","jrsfqzys","jrsfqzfy"]:
    dic[j] = defdic[j]
dic['szgjcs'] = lastParam

saveResponse = conn.post(
    url="https://app.upc.edu.cn/ncov/wap/default/save",
    headers=headers,
    data = dic,
    timeout=10
)

saveJson = json.loads(saveResponse.text)
print(saveJson['m'])

def send_message(message):
    user = signIn['username']
    SCKEY = ""
    data = {"text": f"{user}的: {message}", "desp": ""}
    requests.post(f"https://sctapi.ftqq.com/{SCKEY}.send", data = data)
    

if saveJson['m'] in ['操作成功', '今天已经填报了']:
    pass
else:
    send_message(saveJson['m'])
