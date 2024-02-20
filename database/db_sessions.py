from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import NoResultFound
from database.db_init import engine, Address


def insert_addresses(addresses):
    with Session(bind=engine) as session:

        for address_string in addresses:
            get_existing_address(session, address_string)

        session.commit()


def get_coords(address_string):

    with Session(bind=engine) as session:
        existing_address = get_existing_address(session, address_string)
        
        coords = (existing_address.latitude, existing_address.longitude) \
            if (existing_address.latitude is not None and existing_address.latitude is not None) \
            else None

        session.commit()

    return coords


def insert_coords(address_string, coords):
    with Session(bind=engine) as session:
        existing_address = get_existing_address(session, address_string)

        latitude, longitude = coords

        existing_address.latitude = latitude
        existing_address.longitude = longitude

        session.commit()


def get_existing_address(session, address_string):
    address_string = regularize(address_string)

    # Try to read given address from the table
    # If not exists, add to the table
    try:
        q = session.query(Address).filter_by(string_address=address_string)
        existing_address = q.one()
    except NoResultFound:
        new_address = Address(string_address=address_string)
        session.add(new_address)
        existing_address = new_address
    return existing_address


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
