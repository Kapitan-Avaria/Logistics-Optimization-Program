import pandas as pd
from db_queries import get_objects
from db_init import SegmentStatistics

seg_stats = get_objects(class_name=SegmentStatistics)
df = pd.json_normalize(seg_stats)
df["avg_velocity"] = df["distance"] / (df["duration"] * 60)
seg_id = 11
df_seg = df[df["segment_id"] == seg_id]
df_seg.loc[:, ["avg_velocity"]] = (df_seg["avg_velocity"]-df_seg["avg_velocity"].min())/(df_seg["avg_velocity"].max()-df_seg["avg_velocity"].min())
df_seg.loc[df_seg["segment_id"] == seg_id][["start_time", "avg_velocity"]].groupby("start_time").mean().plot(kind='bar')