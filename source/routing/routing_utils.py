from datetime import datetime


def unix_time_from_hour(hour):
        dt = datetime.strptime(f"{hour}:00", "%H:%M")
        dt_now = datetime.now()
        dt = dt.replace(year=dt_now.year, month=dt_now.month, day=dt_now.day)
        unix_time = int(dt.timestamp())
        return unix_time

def get_unix_time_now(shift=30):
        return datetime.now().timestamp() + shift