from datetime import datetime, timedelta
from source.database.db_init import Segment, Address
from source.database.db_sessions import get_objects, insert_segment_statistics


def _build_url(start_coords, end_coords, date, time):
    url = f"https://yandex.ru/maps/?mode=routes&routes[timeDependent][time]={date}T{time}%3A00&rtext={start_coords}~{end_coords}&rtt=auto"
    return url


def _build_coord_string(latitude, longitude):
    return str(latitude) + "%2C" + str(longitude)


def extract_route_duration(time_str: str):
    time_str = time_str.split()
    if 'ч' in time_str:
        hour_ind = time_str.index('ч') - 1
        hours = int(time_str[hour_ind])
    else:
        hours = 0

    if 'мин' in time_str:
        minutes_ind = time_str.index('мин') - 1
        minutes = int(time_str[minutes_ind])
    else:
        minutes = 0
    
    route_duration = int(hours)*60 + int(minutes)
    return route_duration


def extract_route_distance(dist_str: str):
    dist_str = dist_str.split(' ')
    if 'км' in dist_str:
        km_ind = dist_str.index('км') - 1
        kilometers = float(dist_str[km_ind].replace(',', '.'))
    else:
        kilometers = 0.

    if 'м' in dist_str:
        m_ind = dist_str.index('м') - 1
        meters = float(dist_str[m_ind].replace(',', '.'))
    else:
        meters = 0

    route_distance = int(kilometers * 1000 + meters)
    return route_distance


def insert_data(segment_id, dist_row, time_row, date, start_hour):
    route_distance = extract_route_distance(dist_row)
    route_duration = extract_route_duration(time_row)

    insert_segment_statistics(
        segment_id=segment_id,
        route_distance=route_distance,
        route_duration=route_duration,
        date=date,
        start_time=datetime.strptime(f'{start_hour}:00', '%H:%M').time(),
        week_day=date.weekday(),
        json_response=None,
    )


def generate_urls_bulk(segments: list[Segment], dates_list: list, times_list: list[int]):
    urls_to_parse = []
    for segment in segments:
        address_1 = get_objects(class_name=Address, id=segment['address_1_id'])[0]
        address_2 = get_objects(class_name=Address, id=segment['address_2_id'])[0]
        start_coords = _build_coord_string(address_1['latitude'], address_1['longitude'])
        end_coords = _build_coord_string(address_2['latitude'], address_2['longitude'])
        for date in dates_list:
            for t in times_list:
                if t < 10:
                    h = "0" + str(t)
                else:
                    h = str(t)
                time = h + "%3A" + "00"
                url = _build_url(start_coords, end_coords, date.strftime("%Y-%m-%d"), time)
                print(url)

                urls_to_parse.append((url, date, t, segment['id']))
                
    return urls_to_parse


if __name__ == '__main__':
    segments = get_objects(class_name=Segment)
    dates_list = [(datetime.now() + timedelta(days=1)).date()]
    times_list = [i for i in range(6, 24)]
    generate_urls_bulk(segments, dates_list, times_list)
