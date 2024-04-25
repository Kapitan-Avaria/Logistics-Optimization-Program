from datetime import datetime
from time import sleep
from yandex_in_browser_routing_tools import extract_route_distance, extract_route_duration



class YandexManualRoutingHelper:
    def parse_urls(urls):
        for url, date, t, segment_id in urls:
            print(url)  # Мб вместо этого сделать автокопирование в буфер обмена
            sleep(0.2)
            time_row = input('>>> ')
            input()
            distance_row = input()
            print()
            sleep(0.2)
            
            route_distance = extract_route_distance(distance_row)
            route_duration = extract_route_duration(time_row)

            insert_segment_statistics(
                segment_id=segment_id,
                route_distance=route_distance,
                route_duration=route_duration,
                date=date,
                start_time=datetime.strptime(f'{t}:00', '%H:%M').time(),
                week_day=date.weekday(),
                json_response=None,
            )

