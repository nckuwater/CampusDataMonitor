import requests
import json
import pprint
import datetime
import sqlite3


class CampusDataMonitor:
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


if __name__ == '__main__':
    place = '計網中心_1F自動門_進'
    cdm = CampusDataMonitor()
    cdm.get_date_data(place)

    cdm.get_relative_date_data(place, datetime.datetime.now(), 12)
