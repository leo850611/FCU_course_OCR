# coding=utf-8
import requests
import re
from PIL import Image,ImageFilter
import subprocess
## Copyright (C) 2016 Leo Sheu. <loli>

#NID帳密
nid = 'D0380000'
password = 'abc123'

header = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-TW,zh;q=0.8,en-US;q=0.5,en;q=0.3',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0'
}

reg = r'<input type="hidden" name="(.*)" id="(.*)" value="(.*)" />'
get_value = re.compile(reg)
session = requests.Session()
flag = 0
while flag == 0:
#選課系統首頁
    start = session.get("https://course.fcu.edu.tw/",headers = header)
    all_value = get_value.findall(start.content.decode("utf-8"))

#取得圖形驗證碼
    get_code = session.get("https://course.fcu.edu.tw/validateCode.aspx",headers = header)

    with open("code.png", 'wb') as fp:
        fp.write(get_code.content)
    image = Image.open("code.png").convert('L')
    image = image.point(lambda x: 0 if x<110 else 255)
    #image = image.point(lambda i: i * 1)
    image = image.filter(ImageFilter.DETAIL)
    image = image.crop((5, 3, 43, 18))
    imageNew = Image.open("0.png")
    imageNew.paste(image,(5,3))
    imageNew.save("decode.png")
    subprocess.call(["tesseract.exe","decode.png","out"])
    outputFile = open("out.txt",'r')
    content = outputFile.read(4)
    outputFile.close()

    logininfo = {
        '__EVENTTARGET' :'ctl00$Login1$LoginButton',
        '__EVENTARGUMENT' : '',
        '__LASTFOCUS' : '',
        '__VIEWSTATE' : all_value[3][2],
        '__VIEWSTATEGENERATOR' : all_value[4][2],
        '__EVENTVALIDATION' : all_value[5][2],
        'ctl00$Login1$RadioButtonList1' : 'zh-tw',
        'ctl00$Login1$UserName' : nid,
        'ctl00$Login1$Password' : password,
        'ctl00$Login1$vcode' : content,
        'ctl00$temp':''
    }

#送出登入資料
    login = session.post("https://course.fcu.edu.tw/Login.aspx", data = logininfo)
    neturl = (login.url[0:33] + 'NetPreSelect.aspx' + login.url[33:])

    if '目前不是開放時間' in (login.text):
        flag = 1
        print (login.url)
        print ('登入成功')
    else :
        print ('登入失敗')
