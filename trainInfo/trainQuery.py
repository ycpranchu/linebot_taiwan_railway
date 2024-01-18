import requests 
import pandas as pd
import ptx_info
import csv

app_id = 'ycpin0624-3f23df5b-7375-474b'
app_key = '503b7320-ed7c-4989-800a-6fa51af60cbd'

def trainQuery(user_id, start_station, end_station, ride_date, start_time, end_time):
        
    start_station = start_station.replace('台', '臺', 1)
    end_station = end_station.replace('台', '臺', 1)
    
    table = pd.read_csv("trainInfo/trainCode.csv")
    start_code = str(table.loc[table['車站'] == start_station, '代碼'].iloc[0])
    end_code = str(table.loc[table['車站'] == end_station, '代碼'].iloc[0])

    auth_url="https://tdx.transportdata.tw/auth/realms/TDXConnect/protocol/openid-connect/token"
    url_data = "https://tdx.transportdata.tw/api/basic/v3/Rail/TRA/DailyTrainTimetable/OD/Inclusive/" + start_code + "/to/" + end_code + "/" + ride_date + "?format=JSON"
    url_price = "https://tdx.transportdata.tw/api/basic/v3/Rail/TRA/ODFare/" + start_code + "/to/" + end_code + "?format=JSON"

    a = ptx_info.Auth(app_id, app_key)
    auth_response = requests.post(auth_url, a.get_auth_header())
    
    d = ptx_info.Data(app_id, app_key, auth_response)

    data_response = requests.get(url_data, headers=d.get_data_header())  
    price_response = requests.get(url_price, headers=d.get_data_header())

    with open('trainInfo/trainData/' + user_id + '_trainData.csv', 'w', newline='', encoding='utf-8') as csvfile:
        spamwriter = csv.writer(csvfile, dialect='excel')
        spamwriter.writerow(
            ['日期', '車種車次', '出發站', '抵達站', '出發時間', '抵達時間', '經由', '票價', '訂票', 'booking'])

        data = data_response.json()
        price_data = price_response.json()

        train_price = dict()
        for p in price_data["ODFares"]:
            if p["TrainType"] in train_price:
                train_price[p["TrainType"]] = min(train_price[p["TrainType"]], p["Fares"][0]["Price"])
            else:
                train_price[p["TrainType"]] = p["Fares"][0]["Price"]

        for d in data["TrainTimetables"]:

            stopTime = d["StopTimes"]
            departure_time = stopTime[0]["DepartureTime"]
            arrive_time = stopTime[-1]["ArrivalTime"]

            time = int(departure_time.split(':')[0])
            if time < int(start_time) or time >= int(end_time):
                continue
            
            info = d["TrainInfo"]
            train_number = info["TrainNo"]

            trip_code = {0: '不經山海線', 1: '山線', 2: '海線', 3: '成追線'}
            train_code = {1: '太魯閣', 2: '普悠瑪', 3: '自強', 4: '莒光', 5: '復興', 6: '區間', 7: '普快', 10: '區間快', 11: '新自強'}

            try:
                trip_type = trip_code[info["TripLine"]]
                train_type = train_code[int(info["TrainTypeCode"])]
            except:
                continue

            trip_price = str(train_price[int(info["TrainTypeCode"])])

            booking = "可"
            if train_type.find("區間") != -1:
                booking = "不可"
            
            spamwriter.writerow([ride_date, train_type + ' ' + train_number, start_station, end_station, departure_time, arrive_time, trip_type, trip_price, booking])
    
    # format data
    data = pd.read_csv('trainInfo/trainData/' + user_id + '_trainData.csv', engine='python')
    data = data.sort_values(['出發時間'], ascending=True)
    data = data.set_index('日期')
    data.to_csv('trainInfo/trainData/' + user_id + '_trainData.csv', encoding='utf8')
