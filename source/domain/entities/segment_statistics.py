from dataclasses import dataclass
from datetime import date, time


@dataclass
class SegmentStatistics:
    record_id: int
    segment_id: int
    distance: float
    duration: float
    date: date
    start_time: time
    week_day: int
    json_response: dict
