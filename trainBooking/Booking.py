from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import csv
import requests
import json
from bs4 import BeautifulSoup


def booking_oneWay(pId, start_station, end_station, booking_amount, ride_date, booking_train,  booking_like):
    options = Options()
    options.add_argument("--disable-notifications")
    booking_chrome = webdriver.Chrome('./chromedriver', chrome_options=options)
    booking_chrome.get(
        "https://www.railway.gov.tw/tra-tip-web/tip/tip001/tip121/query")

    pid = booking_chrome.find_elements_by_id('pid')  # 身分證字號
    startStation = booking_chrome.find_element_by_id('startStation')  # 出發站
    endStation = booking_chrome.find_element_by_id('endStation')  # 抵達站
    active = booking_chrome.find_element_by_xpath(
        '//*[@id="queryForm"]/div[1]/div[1]/div[5]/div[2]/label[1]')  # 行程類型
    seatQty = booking_chrome.find_element_by_xpath(
        '//*[@id = "normalQty"]')  # 一般座票數
    rideDate = booking_chrome.find_element_by_xpath(
        '//*[@id="rideDate1"]')  # 日期
    trainNoList1 = booking_chrome.find_element_by_xpath(
        '//*[@id="trainNoList1"]')  # 車次1
    chgSeat1 = booking_chrome.find_element_by_xpath(
        '//*[@id = "queryForm"]/div[2]/div[2]/div[5]/div[2]/div/label')  # 座位偏好
    submit = booking_chrome.find_element_by_xpath(
        '//*[@id="queryForm"]/div[4]/input[2]')  # 訂票

    pid[0].send_keys(pId)
    startStation.send_keys(start_station)
    endStation.send_keys(end_station)
    active.click()
    seatQty.clear()
    seatQty.send_keys(booking_amount)
    rideDate.clear()
    rideDate.send_keys(ride_date)
    trainNoList1.send_keys(booking_train)
    if booking_like == 2:
        chgSeat1.click()

    url1 = 'https://2captcha.com/in.php?key=5d3e2728f225a5acfc668156e0296a4a&method=userrecaptcha&googlekey=6LcgypgUAAAAACk7ULMauOBXRqBgyvWRYH9UimHQ&pageurl=https://www.railway.gov.tw/tra-tip-web/tip/tip001/tip121/query&json=1'
    response = requests.get(url1)  # ReCaptcha 破解step1
    url2 = 'https://2captcha.com/res.php?key=5d3e2728f225a5acfc668156e0296a4a&action=get&id=' + \
        response.json()["request"]+'&json=1'

    time.sleep(30)
    response = requests.get(url2)  # ReCaptcha 破解step2
    booking_chrome.execute_script(
        'document.getElementById("g-recaptcha-response").innerHTML="' + response.json()["request"] + '";')
    submit.submit()

    booking_soup = BeautifulSoup(booking_chrome.page_source, 'lxml')
    booking_wan = booking_soup.find('div', class_="alert alert-warning")
    booking_data = booking_soup.find('div', class_="cartlist-id")
    print('訂票代碼：' + booking_data.find('span').text,
          '請於' + booking_wan.find('span').text)


print('可訂票車次：')
with open('指定列車資料.csv', newline='') as csvfile:
    rows = csv.DictReader(csvfile)
    for row in rows:
        if row['訂票'] == '可':
            print('{:7s}'.format(row['車種車次']), row['出發時間'] + '出發', row['抵達時間'] + '抵達',
                  '行駛時長：' + row['行駛時長'], '票價(全票/孩童票/敬老票)：' + row['全票'], row['孩童票'], row['敬老票'], sep='\t')

booking_train = input('預訂票之車次:')
with open('指定列車資料.csv', newline='') as csvfile:
    rows = csv.DictReader(csvfile)
    for row in rows:
        if booking_train in row['車種車次']:
            start_station = row['出發站']
            end_station = row['抵達站']
            ride_date = row['日期']
            ride_date = ride_date.replace('/', '')

# pId = input('身分證字號：')
booking_type = input('車票種類：(1. 單程/2. 去回)')
booking_amount = eval(input('車票數：'))
booking_like = input('同班車換座：(1. 可/2. 否)')

pId = 'B123464246'
booking_type = '1'
booking_amount = 2
booking_like = '2'

if booking_type == '1':
    booking_oneWay(pId, start_station, end_station, booking_amount,
                   ride_date, booking_train, booking_like)
