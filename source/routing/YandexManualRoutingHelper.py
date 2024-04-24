from datetime import datetime, timedelta
from time import sleep

from source.database.db_init import Segment, Address
from source.database.db_sessions import insert_segment_statistics, get_objects


def build_url(start_coords, end_coords, date, time):
    url = f"https://yandex.ru/maps/?mode=routes&routes[timeDependent][time]={date}T{time}%3A00&rtext={start_coords}~{end_coords}&rtt=auto"
    return url


def build_coord_string(latitude, longitude):
    return str(latitude) + "%2C" + str(longitude)


def generate_urls_bulk(segments: list[Segment], dates_list: list, times_list: list[int]):
    for segment in segments:
        address_1 = get_objects(class_name=Address, id=segment['address_1_id'])[0]
        address_2 = get_objects(class_name=Address, id=segment['address_2_id'])[0]
        start_coords = build_coord_string(address_1['latitude'], address_1['longitude'])
        end_coords = build_coord_string(address_2['latitude'], address_2['longitude'])
        for date in dates_list:
            for t in times_list:
                if t < 10:
                    h = "0" + str(t)
                else:
                    h = str(t)
                time = h + "%3A" + "00"
                url = build_url(start_coords, end_coords, date.strftime("%Y-%m-%d"), time)
                print(url)
                sleep(0.2)
                time_row = input('>>> ').split(' ')
                input()
                distance_row = input().split(' ')
                sleep(0.2)
                if 'ч' in time_row:
                    hour_ind = time_row.index('ч') - 1
                    hours = int(time_row[hour_ind])
                else:
                    hours = 0

                if 'мин' in time_row:
                    minutes_ind = time_row.index('мин') - 1
                    minutes = int(time_row[minutes_ind])
                else:
                    minutes = 0

                if 'км' in distance_row:
                    km_ind = distance_row.index('км') - 1
                    kilometers = float(distance_row[km_ind].replace(',', '.'))
                else:
                    kilometers = 0.

                if 'м' in distance_row:
                    m_ind = distance_row.index('м') - 1
                    meters = float(distance_row[m_ind].replace(',', '.'))
                else:
                    meters = 0

                route_duration = int(hours)*60 + int(minutes)
                route_distance = int(kilometers * 1000 + meters)

                insert_segment_statistics(
                    segment_id=segment['id'],
                    route_distance=route_distance,
                    route_duration=route_duration,
                    date=date,
                    start_time=datetime.strptime(f'{t}:00', '%H:%M').time(),
                    week_day=date.weekday(),
                    json_response=None,
                )


if __name__ == '__main__':
    segments = get_objects(class_name=Segment)
    dates_list = [(datetime.now() + timedelta(days=1)).date()]
    times_list = [i for i in range(6, 24)]
    generate_urls_bulk(segments, dates_list, times_list)
