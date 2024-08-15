from datetime import datetime
from time import sleep
from source.routing.yandex_in_browser_routing_tools import insert_data


class YandexManualRoutingHelper:
    def parse_urls(urls):
        for url, date, t, segment_id in urls:
            print(url)  # Мб вместо этого сделать автокопирование в буфер обмена
            sleep(0.2)
            time_row = input('>>> ')
            input()
            dist_row = input()
            print()

            insert_data(segment_id, dist_row, time_row, date, t)
            sleep(0.2)

