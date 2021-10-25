import grequests
import requests
import json
import pprint
import time
import datetime
import sqlite3
import matplotlib.pyplot as plt


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

    def get_date_data(self, place_name, start_date=datetime.date.today(), end_date=datetime.date.today()):
        url_config = {
            'place': place_name,
            'startdate': start_date.strftime('%Y-%m-%d %H:%M:%S'),
            'enddate': end_date.strftime('%Y-%m-%d %H:%M:%S')
        }

        url = eval(f"f'{self.url_template}'", url_config)
        res = requests.get(url)
        data = eval(res.content)

        # # for debugging
        # with open(f"./data/{url_config['place']}_{url_config['startdate']}_{url_config['enddate']}.json".replace(
        #         ':', '-'), 'w') as fw:
        #     json.dump(data, fw, indent=4)

        return data

    def get_relative_date_data(self, place_name, end_date, hours):
        start_date = end_date - datetime.timedelta(hours=hours)
        data = self.get_date_data(place_name, start_date, end_date)

        # # for debugging
        # url_config = {
        #     'place': place_name,
        #     'startdate': start_date.strftime('%Y-%m-%d %H:%M:%S'),
        #     'enddate': end_date.strftime('%Y-%m-%d %H:%M:%S')
        # }
        # with open(f"./data/delta_{url_config['place']}_{url_config['startdate']}_{url_config['enddate']}.json".replace(
        #         ':', '-'), 'w') as fw:
        #     json.dump(data, fw, indent=4)

        return data

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
        # print(res_list)
        datas = []
        for rs in res_list:
            if rs is not None:
                data = eval(rs.content)
            else:
                print('request got none')
                data = []
            datas.append(data)

        return datas, res_list

    def get_relative_date_datas_fast(self, place_names, end_date, hours):
        start_date = end_date - datetime.timedelta(hours=hours)
        datas, res_list = self.get_date_datas_fast(place_names, start_date, end_date)

        return datas, res_list

    @staticmethod
    def time_interval_index(times, t_time):
        for i in range(len(times) - 1):
            if times[i] < t_time < times[i + 1]:
                return i
        return len(times) - 1

    def divide_data_into_timegroups(self, data, start_time, interval=60, end_time=None):
        """
            Divide data into timegroups by given start_time, interval, end_time
            times = [start_time, start_time+1*interval,..., start_time+n*interval]
            start_time+n*interval >= end_time
        """
        if end_time is None:
            end_time = datetime.datetime.combine(datetime.date.today(), datetime.time()) + datetime.timedelta(days=1)

        if type(start_time) == datetime.date:
            itime = datetime.datetime(start_time.year, start_time.month, start_time.day)
        elif type(start_time) == datetime.datetime:
            itime = start_time
        else:
            raise Exception("Wrong start_time type")

        if type(interval) == int:
            interval = datetime.timedelta(minutes=interval)

        times = [itime]
        groups = [[]]
        group_sums = [0]
        while itime < end_time:
            # itime should >= end_time
            # print(itime)
            itime += interval
            times.append(itime)
            groups.append([])
            group_sums.append(0)

        for info in data:
            # "t_time": "2021-10-21 13:27:20",
            t_time = info.get('t_time')
            if t_time is None:
                continue

            t_time = datetime.datetime.strptime(t_time, "%Y-%m-%d %H:%M:%S")
            ind = self.time_interval_index(times, t_time)
            if ind is None:
                continue

            groups[ind].append(info)
            group_sums[ind] += 1

        return groups, group_sums, times

    def plot_animate(self, place):
        plt.ion()
        plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei']
        plt.rcParams['axes.unicode_minus'] = False
        while True:
            print('loop')
            rdata = self.get_relative_date_data(place, datetime.datetime.now(), 12)
            g, gs, ts = self.divide_data_into_timegroups(rdata, datetime.date.today())

            gs = gs[:-1]
            ts = ts[:-1]
            ts_names = []
            for t in ts:
                ts_names.append(t.strftime('%H:%M'))
            plt.plot(ts_names, gs)
            for i, j in zip(ts_names, gs):
                if j != 0:
                    plt.annotate(str(j), xy=(i, j + 0.5))
            plt.draw()
            plt.suptitle(f'{place} 門禁刷卡統計')
            plt.title(datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S"))
            plt.xlabel('時段')
            plt.ylabel('刷卡人數')
            plt.pause(1)
            plt.clf()


if __name__ == '__main__':
    place = '計網中心_1F自動門_進'
    cdm = CampusDataMonitor()
    cdm.get_date_data(place)

    rdata = cdm.get_relative_date_data(place, datetime.datetime.now(), 12)
    g, gs, ts = cdm.divide_data_into_timegroups(rdata, datetime.date.today())

    gs = gs[:-1]
    ts = ts[:-1]
    ts_names = []
    for t in ts:
        ts_names.append(t.strftime('%H:%M'))
    # pprint.pp(list(zip(ts_names, gs)))
    # cdm.plot_animate(place)

    t = time.time()
    rdata, rres_list = cdm.get_relative_date_datas_fast(list(cdm.location_names.keys()), datetime.datetime.now(), 12)
    success = 0
    fail = 0
    for rres in rres_list:
        if rres.status_code == 200:
            success += 1
        else:
            fail += 1

    print(f'success: {success}, failed: {fail}')
    print(len(rdata))
    print('time cost:', time.time() - t, '(s)')
    rsum = []
    for rd in rdata:
        rsum.append(len(rd))
    pprint.pprint(list(zip(list(cdm.location_names.keys()), rsum)))
