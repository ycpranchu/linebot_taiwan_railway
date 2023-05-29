from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import requests
from bs4 import BeautifulSoup
from abc import ABC, abstractmethod
import os
import csv
import numpy as np
import pandas as pd
import datetime


def trainQuery(user_id, start_station, end_station, ride_date, start_time, end_time):

    GOOGLE_CHROME_PATH = '/app/.apt/usr/bin/google_chrome'
    CHROMEDRIVER_PATH = '/app/.chromedriver/bin/chromedriver'
    
    chrome_bin = os.environ.get('GOOGLE_CHROME_PATH', None)
    option = Options()
    option.binary_location = chrome_bin
    option.add_argument('--disable-gpu')
    option.add_argument('--no-sandbox')
    option.add_argument("--disable-notifications")

    gobytime_chrome = webdriver.Chrome(executable_path="C:/Users/ycpin/我的雲端硬碟/Side Project/trainlinebot-ycpin/trainInfo/chromedriver", options=option)
    gobytime_chrome.get(
        "https://www.railway.gov.tw/tra-tip-web/tip/tip001/tip112/gobytime")  # 依時刻

    start_station = start_station.replace('台', '臺', 1)
    end_station = end_station.replace('台', '臺', 1)
    with open('trainCode.csv', encoding='utf-8') as csvfile:
        rows = csv.DictReader(csvfile)
        for row in rows:
            if row['車站'] == start_station:
                start_station = row['代碼']
            if row['車站'] == end_station:
                end_station = row['代碼']

    option = '1'
    early_bird_button = 2
    train_type_list = str(1)
    start_or_endTime = str(1)

    startStation = gobytime_chrome.find_element_by_id(
        'startStation')  # 出發站
    endStation = gobytime_chrome.find_element_by_id('endStation')  # 抵達站
    option_btn = gobytime_chrome.find_elements_by_xpath(
        '//*[@id="queryForm"]/div[1]/div[1]/div[5]/div[2]/label' + '[' + option + ']')  # 轉乘條件

    rideDate = gobytime_chrome.find_element_by_id('rideDate')  # 日期
    startOrEndTime = gobytime_chrome.find_element_by_id(
        'startOrEndTime' + start_or_endTime)  # 查詢條件
    startTime = gobytime_chrome.find_element_by_id('startTime')  # 時段起
    endTime = gobytime_chrome.find_element_by_id('endTime')  # 時段迄

    trainTypeList = gobytime_chrome.find_element_by_xpath(
        '//*[@id="queryForm"]/div[1]/div[3]/div[1]/div[2]/label' + '[' + train_type_list + ']')  # 車種

    earlyBirdButton = gobytime_chrome.find_element_by_xpath(
        '//*[@id="queryForm"]/div[1]/div[3]/div[2]/div[2]/label')  # 限定早享車次(優惠)

    startStation.send_keys(start_station)
    endStation.send_keys(end_station)
    option_btn[0].click()
    rideDate.clear()
    rideDate.send_keys(ride_date)
    startOrEndTime.click()
    startTime.send_keys(start_time)
    endTime.send_keys(end_time)
    trainTypeList.click()

    if early_bird_button == 1:
        earlyBirdButton.click()

    submit = gobytime_chrome.find_element_by_xpath(
        '//*[@id="queryForm"]/div[1]/div[3]/div[3]/input')  # 查詢
    submit.submit()

    gobytime_soup = BeautifulSoup(gobytime_chrome.page_source, 'lxml')
    gobytime_html = gobytime_soup.find_all('tr', class_='trip-column')

    with open('trainInfo/trainData/' + user_id + '_trainData.csv', 'w', newline='', encoding='utf-8') as csvfile:
        spamwriter = csv.writer(csvfile, dialect='excel')
        spamwriter.writerow(
            ['日期', '車種車次', '出發站', '抵達站', '始發站', '終點站', '出發時間', '抵達時間', '行駛時長', '經由', '全票', '孩童票', '敬老票', '訂票'])

        for data in gobytime_html:
            dict = {}
            train_number = data.find('a').text
            dict['train_number'] = train_number
            location = data.find_all('span', class_='location')
            dict['from'] = location[0].text
            dict['to'] = location[1].text
            imformation = data.find_all('td')
            dict['departure_time'] = imformation[1].text
            dict['arrive_time'] = imformation[2].text
            dict['take_time'] = imformation[3].text
            dict['type'] = imformation[4].text
            dict['audlt_ticket'] = imformation[6].find('span').text
            dict['child_ticket'] = imformation[7].find('span').text
            dict['senior_ticket'] = imformation[8].find('span').text

            if train_number[0:2] != '區間':
                dict['booking'] = '可'
            else:
                dict['booking'] = ''

            spamwriter.writerow([ride_date, dict['train_number'], start_station, end_station, dict['from'], dict['to'], dict['departure_time'], dict['arrive_time'],
                                 dict['take_time'], dict['type'], dict['audlt_ticket'], dict['child_ticket'], dict['senior_ticket'], dict['booking']])

    gobytime_chrome.quit()


data_input = "9/5 12 15 彰化 台中".split(' ')

date = data_input[0].split('/')
if len(date[0]) != 4:
    date.insert(0, str(datetime.datetime.now().year))
if len(date[1]) != 2:
    date[1] = '0' + date[1]
if len(date[2]) != 2:
    date[2] = '0' + date[2]
ride_date = '-'.join(date)

start_time = data_input[1]
end_time = data_input[2]
start_station = data_input[3]
end_station = data_input[4]

trainQuery("123", start_station, end_station, ride_date, start_time, end_time)
