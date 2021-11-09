import grequests
import requests
import json
import pprint
import time
import datetime
import sqlite3
import concurrent.futures
import pandas as pd
 
class ThreadRequest:
    def load_url(self, url, timeout):
        return requests.get(url, timeout=timeout)

    def get_urls(self, urls):
        datas = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            resp_err = 0
            resp_ok = 0
            future_to_url = {executor.submit(self.load_url, url, 10): url for url in urls}
            for future in concurrent.futures.as_completed(future_to_url):
                url = future_to_url[future]
                # print(url)
                try:
                    data = future.result()
                    datas.append(data)
                except Exception as exc:
                    resp_err = resp_err + 1
                else:
                    resp_ok = resp_ok + 1
        return datas


class CampusDataMonitor:
    """
        "EmpNo": "學號",
        "0": "學號",
        "EmpName": "姓名",
        "1": "姓名",
        "DeptNo": "系所編號",
        "2": "系所編號",
        "DeptName": "系所名稱",
        "3": "系所名稱",
        "CardNo": "卡號",
        "4": "卡號",
        "DoorName": "門名",
        "5": "門名",
        "t_time": "2021-10-21 13:29:35",          刷卡時間
        "6": "Oct 21 2021 01:29:35:000PM",        刷卡時間
        "InOut": "\u9032",                        進/出
        "7": "\u9032",
        "t_RecvTime": "2021-10-21 13:29:39",      上傳時間
        "8": "Oct 21 2021 01:29:39:327PM",        上傳時間
        "OGAttGroup": "\u8a08\u7db2\u4e2d\u5fc3", 管制區域
        "9": "\u8a08\u7db2\u4e2d\u5fc3"           管制區域
    """

    url_template = None
    location_names = {}  # location: group

    def __init__(self, url_path='./config/ncku_api_url.txt',
                 location_names_path='./config/ogwebbasesetting_ogattlistctrl_ascx_211021.csv'):
        with open('./config/ncku_api_url.txt', 'r') as fr:
            self.url_template = fr.read()

        with open(location_names_path, 'r', encoding='utf8') as fr:
            location_name_lines = fr.read().split('\n')[1:]
        self.location_names = {'雲平大樓_B1駐警隊監控機房':'光復校區 雲平大樓',
                                '雲平大樓_西棟B1梯間':'光復校區 雲平大樓',
                                '雲平大樓_西棟B2梯間':'光復校區 雲平大樓',
                                '雲平大樓_西棟電梯-右':	'光復校區 雲平大樓',
                                '雲平大樓_西棟電梯-左':	'光復校區 雲平大樓',
                                '雲平大樓_東棟電梯-右':	'光復校區 雲平大樓',
                                '雲平大樓_東棟電梯-左':	'光復校區 雲平大樓',
                                '雲平大樓B1B2廁所GCU':	'光復校區 雲平大樓',
                                '雲平大樓B1男/女廁所':	'光復校區 雲平大樓',
                                '雲平大樓B2女廁所':	'光復校區 雲平大樓',
                                '雲平大樓B2男、無障礙廁所':	'光復校區 雲平大樓',
                                '雲平大樓-電梯GCU':	'光復校區 雲平大樓',
                                '資工系_B1安全門':'成功校區 資訊工程系',
                                '資工系_B2安全門':'成功校區 資訊工程系',
                                '資工系_北側門':'成功校區 資訊工程系',
                                '資工系_南側門':'成功校區 資訊工程系',
                                '資工系新館_1F東大門':'成功校區 資訊工程系',
                                '資工系新館_1F南側門':'成功校區 資訊工程系',
                                '資工系新館G1':'成功校區 資訊工程系',
                                '文學院1F西側門':	'光復校區 文學院修齊大樓',
                                '文學院2F前自動門':	'光復校區 文學院修齊大樓',
                                '文學院2F後自動門':	'光復校區 文學院修齊大樓',
                                '文學院B1電梯'	:'光復校區 文學院修齊大樓',
                                '文學院B2電梯':'光復校區 文學院修齊大樓',
                                '文學院GCU':'光復校區 文學院修齊大樓',
                                '計網中心_1F自動門_出'	:'成功校區 計網中心',
                                '計網中心_1F自動門_進'	:'成功校區 計網中心',
                                '計網中心_2F（防疫）'	:'成功校區 計網中心',
                                '計網中心_2F_75201'	:'成功校區 計網中心',
                                '計網中心_2F_75209'	:'成功校區 計網中心',
                                '計網中心_2F大門'	:'成功校區 計網中心',
                                '計網中心_2F側門'	:'成功校區 計網中心',
                                '計網中心_3F_75301'	:'成功校區 計網中心',
                                '計網中心_3F_75309'	:'成功校區 計網中心',
                                '計網中心_3F側門'	:'成功校區 計網中心',
                                '計網中心_3F會議室'	:'成功校區 計網中心',
                                '計網中心_4F大門'	:'成功校區 計網中心',
                                '計網中心_5F大門':'成功校區 計網中心',
                                '計網中心_GCU(16門）'	:'成功校區 計網中心',
                                '計網中心6F大門' :'成功校區 計網中心',
                                '光復前門機車進-右' : '光復校區 機車通行',
                                '光復前門機車進-左':'光復校區 機車通行',
                                '光一舍GCU':'光復校區 光一舍',
                                '光一舍中間前門':'光復校區 光一舍',
                                '光一舍中間後門':'光復校區 光一舍',
                                '光一舍側門1':'光復校區 光一舍',
                                '光一舍側門2':'光復校區 光一舍',
                                '光一舍側門3':'光復校區 光一舍'}
    
        print('locations count:', len(self.location_names.keys()))
        # self.conn = sqlite3.connect(':memory:')
        # self.c = self.conn.cursor()

    def get_date_datas_fast(self, place_names, start_date=datetime.date.today(), end_date=datetime.date.today()):
        # url_config = {
        #     # 'place': place_name,
        #     'startdate': start_date.strftime('%Y-%m-%d %H:%M:%S'),
        #     'enddate': end_date.strftime('%Y-%m-%d %H:%M:%S')
        # }
        urls = []
        res_list = []
        for place_name in place_names:
            url_config = {
                'place': place_name,
                'startdate': start_date.strftime('%Y-%m-%d %H:%M:%S'),
                'enddate': end_date.strftime('%Y-%m-%d %H:%M:%S')
            }
            url = eval(f"f'{self.url_template}'", url_config)
            urls.append(url)
            res_list.append(grequests.get(url))

        res_list = grequests.map(res_list)
        #afr = ThreadRequest()
        #res_list = afr.get_urls(urls)
        datas = []
        for rs in res_list:
            if rs == None:
                data = None
            else:
                data = eval(rs.content)
            datas.append(data)
        return datas, res_list

    def get_relative_date_datas_fast(self, place_names, end_date, minutes):
        start_date = end_date - datetime.timedelta(minutes=minutes)
        datas, res_list = self.get_date_datas_fast(place_names, start_date, end_date)

        return datas, res_list

def Take_Data_Now(cdm):
    t = time.time()
    tonow = tonow = datetime.datetime.now()
    minute_passed = tonow.hour*60 + tonow.minute
    rdata, rres_list = cdm.get_relative_date_datas_fast(list(cdm.location_names.keys()), datetime.datetime.now(),
                                                            minute_passed)
    success = 0
    fail = 0
    for rres in rres_list:
        if rres==None:
            fail+=1
        else:
            if rres.status_code == 200:
                success += 1
            else: 
                fail += 1
    rsum = []
    for rd in rdata:
        if rd==None:
            rsum.append(0)
        else:
            rsum.append(len(rd))
    time_cost=time.time()-t
    machine_name=[]
    for i in range(len(rsum)):
        machine_name.append(list(cdm.location_names.keys())[i])
    dic={
    "門機名稱" : machine_name,
    "人數" : rsum
    }
    location_names_path='./config/ogwebbasesetting_ogattlistctrl_ascx_211021.csv'
    csv_data=pd.read_csv(location_names_path)
    data=pd.DataFrame(csv_data)
    Data_handled=['光復校區 雲平大樓','成功校區 資訊工程系','光復校區 文學院修齊大樓','成功校區 計網中心','光復校區 機車通行','光復校區 光一舍']
    n=[]
    result=[['光復校區 雲平大樓',0],['成功校區 資訊工程系',0],['光復校區 文學院修齊大樓',0],['成功校區 計網中心',0],['光復校區 機車通行',0],['光復校區 光一舍',0]]
    for i in range(len(Data_handled)):
        n.append([0,0,0])
    #construc a dictionary of 管制區域:[人數,經度,緯度]
    for i in range(len(rsum)):
        for j in range(len(result)):
            if(result[j][0]==list(data[(data['門名']==list(cdm.location_names.keys())[i])]['管制區域'])[0]):
                result[j][1]+=rsum[i]
    return result,time_cost
if __name__ == '__main__':
    cdm = CampusDataMonitor()
    while True:
        result=Take_Data_Now(cdm)
        print(result)
        time.sleep(5)
        