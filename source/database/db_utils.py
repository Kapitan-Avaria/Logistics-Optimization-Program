from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm import Session as SessionClass

from source.database.db_init import Session
import numpy as np


def use_with_session(func):
    """Decorator function that wraps the func with 'with Session() ... session.commit()',
    if 'session' argument is not provided"""

    def wrapper(*args, **kwargs):
        # If existing session provided, continues with default function behaviour
        if "session" in kwargs.keys() or (True in map(lambda x: isinstance(x, SessionClass), args) if len(args) > 0 else False):
            return func(*args, **kwargs)

        # If the session is not provided, creates new one
        with Session() as session:
            ret = func(*args, **kwargs, session=session)
            session.commit()
        return ret

    return wrapper


def extract_object_as_dict(obj):
    res: dict = obj.__dict__
    res.pop('_sa_instance_state', None)
    return res


def select_existing_object(session: Session, class_name, **kwargs):
    for key in kwargs.keys():
        if isinstance(kwargs[key], str):
            kwargs[key] = regularize(kwargs[key])

    try:
        q = session.query(class_name).filter_by(**kwargs)
        existing_object = q.one()
    except NoResultFound:
        new_object = class_name(**kwargs)
        session.add(new_object)
        existing_object = new_object
    session.flush()
    return existing_object


def select_many_objects(session: Session, class_name, **kwargs):
    for key in kwargs.keys():
        if isinstance(kwargs[key], str):
            kwargs[key] = regularize(kwargs[key])

    q = session.query(class_name).filter_by(**kwargs)
    objects = q.all()

    return objects


def calc_direct_distances(lat1: np.ndarray, lon1: np.ndarray, lat2: np.ndarray, lon2: np.ndarray) -> np.ndarray:
    """
    Calculate the great circle distance in kilometers between two points
    on the earth (specified in decimal degrees)
    """
    # Convert decimal degrees to radians
    # lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    lat1 = np.radians(lat1)
    lon1 = np.radians(lon1)
    lat2 = np.radians(lat2)
    lon2 = np.radians(lon2)

    # Haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
    c = 2 * np.arcsin(np.sqrt(a))
    r = 6371 * 1000  # Radius of earth in meters.
    return c * r


def read_strings_input():
    arr = []

    s = input()

    while s != '':
        arr.append(s)
        s = input()
    return arr


def regularize(s: str):
    # Заменяем нестандартные пробельные символы обычным пробелом
    s = s.replace('\xa0', ' ')

    # Заменяем идущие подряд пробелы одним пробелом
    s = ' '.join(s.split())
    return s
