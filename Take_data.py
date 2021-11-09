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

        i = 0
        for line in location_name_lines:
            # i += 1
            # if i > 10:
            #     break
            if line == '':
                continue
            line = line.split(',')
            self.location_names[line[0]] = line[1]

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
            #res_list.append(grequests.get(url))

        #res_list = grequests.map(res_list)
        afr = ThreadRequest()
        res_list = afr.get_urls(urls)
        datas = []
        for rs in res_list:
            if rs == None:
                data = None
            else:
                data = eval(rs.content)
            datas.append(data)
        return datas, res_list

    def get_relative_date_datas_fast(self, place_names, end_date, s):
        start_date = end_date - datetime.timedelta(seconds=s)
        datas, res_list = self.get_date_datas_fast(place_names, start_date, end_date)

        return datas, res_list

def Take_Data_Now(cdm):
    t = time.time()
    rdata, rres_list = cdm.get_relative_date_datas_fast(list(cdm.location_names.keys()), datetime.datetime.now(),30)
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

    print(f'success: {success}, failed: {fail}')
    #print(len(rdata))
    time_cost=time.time()-t
    print('time cost:', time_cost, '(s)')
    rsum = []
    for rd in rdata:
        if rd==None:
            rsum.append(0)
        else:
            rsum.append(len(rd))
    #pprint.pprint(list(zip(list(cdm.location_names.keys()), rsum)))
    for i in range(len(rsum)):
        if(rsum[i]>0):
            print(list(cdm.location_names.keys())[i],' : ',rsum[i])
    print("************************************************")
    machine_name=[]
    for i in range(len(rsum)):
        machine_name.append(list(cdm.location_names.keys())[i])
    dic={
    "門機名稱" : machine_name,
    "人數" : rsum
    }
    #每個'門名'都會有對應的'管制區域'
    location_names_path='./config/ogwebbasesetting_ogattlistctrl_ascx_211021.csv'
    location_lng_lat='個場所對應經緯度.xlsx'
    xlsx_data=pd.read_excel(location_lng_lat)
    csv_data=pd.read_csv(location_names_path)
    data=pd.DataFrame(csv_data) # stored all '門名',total 562 '門名'
    location_data=pd.DataFrame(xlsx_data) # store the latitude and longitude corresponding to all '管制區域'
    Data_handled=data['管制區域'].unique() # store the unique '管制區域'
    n=[]
    result=[]
    c=0
    #初始化 Location_dic ,用來儲存各個管制區域對應的刷卡人數
    for i in range(len(Data_handled)):
        n.append([0,0,0])
    Location_dic=dict(zip(Data_handled,n))
    #construc a dictionary of 管制區域:[經度,緯度,人數]************************************************************
    for i in range(len(rsum)): 
        #rsum 對應cdm.location_names.key() == 刷卡人數對應門名
        #list(cdm.location_names.keys())[i] == 第i個'門名'
        #rsum == 第i個刷卡人數
        #data 為門名對應管制區域，所以透過data來求各個門名的對應管制區域
        Location_dic[list(data[(data['門名']==list(cdm.location_names.keys())[i])]['管制區域'])[0]][2]+=rsum[i]
        Location_dic[list(data[(data['門名']==list(cdm.location_names.keys())[i])]['管制區域'])[0]][0] = float(location_data[(location_data['管制區域']==list(data[(data['門名']==list(cdm.location_names.keys())[i])]['管制區域'])[0])]['經緯度'].str.split(',').str.get(0))
        Location_dic[list(data[(data['門名']==list(cdm.location_names.keys())[i])]['管制區域'])[0]][1] = float(location_data[(location_data['管制區域']==list(data[(data['門名']==list(cdm.location_names.keys())[i])]['管制區域'])[0])]['經緯度'].str.split(',').str.get(1))
        if rsum[i]>0:
            result.append([Location_dic[list(data[(data['門名']==list(cdm.location_names.keys())[i])]['管制區域'])[0]][0],Location_dic[list(data[(data['門名']==list(cdm.location_names.keys())[i])]['管制區域'])[0]][1],rsum[i]/3])
    return result,time_cost#reusult stored the location that have data. data type:2D-list
                            #time_cost stored the time of take data from api
    #*********************************************************************************************************
if __name__ == '__main__':
    cdm = CampusDataMonitor()
    while True:
        result=Take_Data_Now(cdm)
        print(result)
        