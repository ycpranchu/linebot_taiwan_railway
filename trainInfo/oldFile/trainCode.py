# coding = utf-8
# 程式目的：爬取臺鐵所有車站之名稱與代碼，並輸出 trainCode.csv 檔
import csv
import requests
from bs4 import BeautifulSoup

url = "https://www.railway.gov.tw/tra-tip-web/tip/tip001/tip111/view" # 前往指定網站
reqs = requests.get(url)
soup = BeautifulSoup(reqs.text, 'lxml')
stationName = soup.find_all('div', class_='traincode_name1') # 車站名稱
stationCode = soup.find_all('div', class_='traincode_code1') # 車站代碼

with open('trainCode.csv', 'w', newline='', encoding='utf-8') as csvfile:
    spamwriter = csv.writer(csvfile, dialect='excel')
    spamwriter.writerow(['車站', '代碼'])

    for i in range(len(stationName)):
        spamwriter.writerow(
            [stationName[i].text, stationCode[i].text])
