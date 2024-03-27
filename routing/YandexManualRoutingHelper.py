from database.db_sessions import insert_segment_statistics
from database.db_init import Segment


def build_url(start_coords, end_coords, time):
    url = ''


def bulk_url_generator(segments: list, times_list: list):
    for segment in segments:
        for t in times_list:
            # Тут обрабатываем время, дату, день недели для корректной подачи
            build_url()
            insert_segment_statistics()