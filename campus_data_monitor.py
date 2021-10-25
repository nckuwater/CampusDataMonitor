import requests
import json
import pprint
import datetime
import sqlite3


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

    def __init__(self, url_path='./config/ncku_api_url.txt'):
        with open('./config/ncku_api_url.txt') as fr:
            self.url_template = fr.read()

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

        # for debugging
        with open(f"./data/{url_config['place']}_{url_config['startdate']}_{url_config['enddate']}.json".replace(
                ':', '-'), 'w') as fw:
            json.dump(data, fw, indent=4)

        return data

    def get_relative_date_data(self, place_name, end_date, hours):
        start_date = end_date - datetime.timedelta(hours=hours)
        data = self.get_date_data(place_name, start_date, end_date)

        # for debugging
        url_config = {
            'place': place_name,
            'startdate': start_date.strftime('%Y-%m-%d %H:%M:%S'),
            'enddate': end_date.strftime('%Y-%m-%d %H:%M:%S')
        }
        with open(f"./data/delta_{url_config['place']}_{url_config['startdate']}_{url_config['enddate']}.json".replace(
                ':', '-'), 'w') as fw:
            json.dump(data, fw, indent=4)

        return data

    @staticmethod
    def time_interval_index(times, t_time):
        for i in range(len(times) - 1):
            if times[i] < t_time < times[i + 1]:
                return i
        return len(times) - 1

    def divide_data_into_timegroups(self, data, start_time, interval=60, end_time=None):
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


if __name__ == '__main__':
    place = '計網中心_1F自動門_進'
    cdm = CampusDataMonitor()
    cdm.get_date_data(place)

    rdata = cdm.get_relative_date_data(place, datetime.datetime.now(), 12)
    g, gs, ts = cdm.divide_data_into_timegroups(rdata, datetime.date.today())
    pprint.pp(list(zip(ts, gs)))
