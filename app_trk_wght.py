from flask import Flask, jsonify, request
import os
from datetime import datetime
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd


# set the do_debug to run debug mode in local
do_debug = "apicharthortiangtham" in os.getcwd()

# create Flask object
api = Flask(__name__)


# create  api.route
# each route is associated with a function

# สร้าง Home Page
@api.route('/') 
def main():
    return 'Hello This is home page'


# what we can return
# - string
# - dictionary
# - list (import jsonify)
# - webpage (import render_template)


# Receive input from users
@api.route('/tellweight')
def get_param():
    cus_id = request.args.get('customer_id', default='default_id', type=str)
    cus_wt_now = request.args.get('keyword', default='0', type=str)
    try:
        cus_wt_now = float(cus_wt_now)
    except:
        return jsonify({'out_tr_wght': 'ช่วยใส่น้ำหนักเป็นตัวเลขนะ'})

    today_time = datetime.now()

    if cus_wt_now == None:
        return jsonify({'out_tr_wght': 'ลองพิมน้ำหนักปัจจุบันมาสิ'})
    else:
        ###------------------------------------------------###
        ### Get Google Sheet Data                          ###
        ###------------------------------------------------###
        # use creds to create a client to interact with the Google Drive API
        scopes = ['https://spreadsheets.google.com/feeds']

        # creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scopes)
        # client = gspread.authorize(creds)

        json_creds = os.getenv("GOOGLE_SHEETS_CREDS_JSON")
        creds_dict = json.loads(json_creds)
        creds_dict["private_key"] = creds_dict["private_key"].replace("\\\\n", "\n")
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scopes)
        client = gspread.authorize(creds)

        # Find a workbook by url
        # this is the link copied from url bar (not from sharing)
        spreadsheet = client.open_by_url('https://docs.google.com/spreadsheets/d/1atlAVhcdD4ZNtqtt-MzSPvmbmT1s3j_Bh930hKyyFIA/edit#gid=0')
        sheet = spreadsheet.sheet1

        #new_row = [{'date': '2020-10-05', 'customer_id': 'id45678', 'keyword': 55.6}]
        new_row = [today_time.strftime('%Y-%m-%d %H:%M:%S.%f'), cus_id, cus_wt_now]
        sheet.append_row(new_row)

        # Extract and print all of the values
        rows = sheet.get_all_records()
        #print(rows)
        ###------------------------------------------------###
        
        # get previous customer weight from google sheet
        dataframe = pd.DataFrame(rows)
        dataframe.timestamp = pd.to_datetime(dataframe.timestamp)
        dataframe = dataframe[dataframe.customer_id == cus_id]
        if dataframe.shape[0] <= 1:
            return jsonify({'out_tr_wght': 'บันทึกน้ำหนักเป็นครั้งแรกสำเร็จแล้วนะ'})
        dataframe = dataframe.sort_values('timestamp', ascending=False)
        #print(dataframe.iloc[1])
        
        cus_wt_bfr = dataframe.iloc[1].keyword
        date_bfr = str(dataframe.iloc[1].timestamp.date())

        # output string
        output = str('น้ำหนักของคุณเปลี่ยนแปลง ' + str(cus_wt_now-cus_wt_bfr)  + ' กก.'
                    + ' จากเดิม (เดิมวัดเมื่อ ' +  date_bfr + ')')
        return jsonify({'out_tr_wght': output})


if __name__ == '__main__':
    # the following will run only if we run this script directly 
    # (i.e. by running 'python api.py') 

    #api.run()

    # if you want the auto update
    #api.run(debug=True)
    api.run(debug=do_debug)


# # to run this file
# python app_trk_wght.py

# now you can try this on your browser 
# http://127.0.0.1:5000/tellweight?customer_id=123dd&keyword=45
# notice the route is followed by ?
# use & to specify more parameters

## how to read/write to a google sheet from Heroku
# https://www.twilio.com/blog/2017/02/an-easy-way-to-read-and-write-to-a-google-spreadsheet-in-python.html
# https://www.twilio.com/blog/2017/02/an-easy-way-to-read-and-write-to-a-google-spreadsheet-in-python.html

# will continue on implement google sheet api

