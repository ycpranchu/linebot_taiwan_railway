from linebot.models import MessageEvent, TextMessage, TextSendMessage, FlexSendMessage
from linebot.exceptions import InvalidSignatureError
from linebot import LineBotApi, WebhookHandler
from flask import Flask, abort, request
import csv
import numpy as np
import pandas as pd
import json
import datetime
import sys

sys.path.append("./trainInfo")
import trainQuery

app = Flask(__name__)

# LINE 聊天機器人的基本資料
line_bot_api = LineBotApi('jJisTObx7OduP362CboSPS8X3vj9XBeSv8IYFwI8f+/v7EIjZfZkuJtJmigbcNNmgzXEV0WRoKe9h7dMOoU6Un6Q3Mt395VW5b1RgGqgatjfuuWOGT0PXfw7t/vOO3c2G30IA8aVgZ5c4YygTvdLIQdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('428e771830a916031feb0a3f0d239ce5')

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    print(body)
    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_id = event.source.user_id
    if user_id != "Udeadbeefdeadbeefdeadbeefdeadbeef":  # 排除預設資料
        # 輸入：日期 時間 起點 終點

        data_input = event.message.text.split(' ')
        data_path = 'trainInfo/trainData/' + user_id + '_trainData.csv'

        try:
            date = data_input[0].split('/')
            if len(date[0]) != 4:
                if int(date[1]) <= datetime.datetime.now().month and int(date[1]) < datetime.datetime.now().day:
                    date.insert(0, str(datetime.datetime.now().year + 1))
                else:
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

            if not start_time.isdigit():
                raise Exception('')
            if not end_time.isdigit():
                raise Exception('')

        except Exception as e:
            line_bot_api.reply_message(
                event.reply_token, TextSendMessage(text="格式輸入錯誤!\n正確格式為：年(非必填)/月/日 時間 時間 起點 終點"))
            return

        try:
            trainQuery.trainQuery(user_id, start_station, end_station, ride_date, start_time, end_time)
        except:
            line_bot_api.reply_message(
                event.reply_token, TextSendMessage(text="資料輸入錯誤，查詢失敗！"))
        
        # check output data
        with open(data_path, encoding='utf-8') as csvfile:
            rows = csv.DictReader(csvfile)

            if list(rows) == []:
                line_bot_api.reply_message(
                event.reply_token, TextSendMessage(text="查無列車資料，請更改選取範圍!"))

        record_a = []
        record_a.append({
            "type": "text",
            "text": "非訂位車次",
            "weight": "bold",
            "size": "xl",
            "color": "#0066cc"
        })

        elements = []
        output_messages = []
        alt_text = "查詢成功！"

        able_to_booking_file = open('replyMessage/able_to_booking.json', 'r', encoding='utf-8')
        able_input_file = able_to_booking_file.read()  # 可訂票車次顯示格式

        unable_to_booking_file = open('replyMessage/unable_to_booking.json', 'r', encoding='utf-8')
        unable_input_file = unable_to_booking_file.read()  # 不可訂票車次顯示格式

        input_data_count = 0

        # 產生輸出樣式
        with open(data_path, encoding='utf-8') as csvfile:
            rows = csv.DictReader(csvfile)

            for row in rows:
                date = row['日期'].split('-')
                for i in range(0, 3):
                    if date[i][0] == '0':
                        date[i] = date[i][1:]
                dateFormat = date[1] + "月" + date[2] + "日"

                if(row['訂票'] == '可'):  # 可訂票車次
                    able_input_data = json.loads(able_input_file)
                    able_input_data["body"]["contents"][0]["text"] = row['車種車次']
                    able_input_data["body"]["contents"][1]["contents"][0]["contents"][1]["text"] = dateFormat
                    able_input_data["body"]["contents"][1]["contents"][1]["contents"][1]["text"] = row['出發時間'] + ' 至 ' + row['抵達時間']
                    able_input_data["body"]["contents"][1]["contents"][2]["contents"][1]["text"] = row['經由']

                    elements.append(able_input_data)
                else:  # 不可訂票車次
                    unable_input_data = json.loads(unable_input_file)
                    unable_input_data["body"]["contents"][0]["text"] = row['車種車次']
                    unable_input_data["body"]["contents"][1]["contents"][0]["contents"][1]["text"] = dateFormat
                    unable_input_data["body"]["contents"][1]["contents"][1]["contents"][1]["text"] = row['出發時間'] + ' 至 ' + row['抵達時間']
                    unable_input_data["body"]["contents"][1]["contents"][2]["contents"][1]["text"] = row['經由']
                    
                    elements.append(unable_input_data)

                input_data_count += 1

                if input_data_count == 10:
                    output_data = {
                        "type": "carousel",
                        "contents": elements
                    }

                    output_messages.append(FlexSendMessage(alt_text, output_data))
                    elements = []
                    input_data_count = 0

        if input_data_count != 0:
            output_data = {
                "type": "carousel",
                "contents": elements
            }
            output_messages.append(FlexSendMessage(alt_text, output_data))

        able_to_booking_file.close()
        unable_to_booking_file.close()

        line_bot_api.reply_message(event.reply_token, output_messages)

if __name__ == "__main__":
    app.run()