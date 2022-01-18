from requests import request
import ptx_info
import json
import csv
import pandas as pd
import operator

app_id = 'bbdd93559e754dc68c2e502ced7664dc'
app_key = 'fEzsx4juJ6abEZqgCUQgfN9q1wI'


def trainQuery(start_station, end_station, ride_date, start_time, end_time):

    a = ptx_info.Demo(app_id, app_key)
    data_response = request(
        'get', 'https://ptx.transportdata.tw/MOTC/v2/Rail/TRA/DailyTimetable/TrainDate/' + ride_date + '?format=JSON', headers=a.get_auth_header())

    print(data_response.json())

    start_station = start_station.replace('台', '臺', 1)
    end_station = end_station.replace('台', '臺', 1)

    train_code_data = pd.read_csv("trainInfo/trainCode.csv", index_col="車站")
    train_code_data.loc[start_station]
    train_code_data.loc[end_station]

    with open('trainInfo/trainData.csv', 'w', newline='', encoding='utf-8') as csvfile:
        spamwriter = csv.writer(csvfile, dialect='excel')
        spamwriter.writerow(
            ['日期', '車種車次', '出發時間', '抵達時間', '經由', '訂票'])

        for data in data_response.json():

            info = data["DailyTrainInfo"]
            train_number = info["TrainNo"]

            trip_code = {0: '不經山海線', 1: '山線', 2: '海線', 3: '成追線'}
            train_code = {1: '太魯閣', 2: '普悠瑪', 3: '自強',
                          4: '莒光', 5: '復興', 6: '區間', 7: '普快', 10: '區間快'}

            try:
                trip_type = trip_code[info["TripLine"]]
                train_type = train_code[int(info["TrainTypeCode"])]
            except:
                continue

            booking = "可"
            if train_type.find("區間") != -1:
                booking = "不可"

            start = False
            end = False
            departure_time = ""
            arrive_time = ""

            for stopTime in data["StopTimes"]:
                if stopTime["StationName"]["Zh_tw"] == start_station:
                    start = True
                    departure_time = stopTime["DepartureTime"]

                if stopTime["StationName"]["Zh_tw"] == end_station and start == True:
                    arrive_time = stopTime["ArrivalTime"]
                    end = True

            if start and end:
                time = int(departure_time.split(':')[0])

                if time < int(start_time) or time >= int(end_time):
                    continue
                spamwriter.writerow(
                    [ride_date, train_type + ' ' + train_number, departure_time, arrive_time, trip_type, booking])

    # format data
    data = pd.read_csv('trainInfo/trainData.csv', engine='python')
    data = data.sort_values(['出發時間'], ascending=True)
    data = data.set_index('日期')
    data.to_csv('trainInfo/trainData.csv', encoding='utf8')
