from source.database.db_queries import *
from source.database.db_init import db_init

from pathlib import Path
import random


addresses = ['Краснодар Сарабеева 11', 'г.Ставрополь, 1-я Промышленная, 28', 'Адлер, Авиационная ул, 34 (рынок)', 'г Сочи, р-н Адлерский, Станиславского, д. 1/3', 'г Сочи, с Нижняя Шиловка, ул Светогорская, д. 42А', 'Сочи г., Пластунская ул., д. 157/5', 'Дагомыс, Батумское шоссе, 64 А', 'Лазаревское, Лазарева ул, 1/1', 'Туапсе, Богдана Хмельницского ул, 175', 'г Сочи, ул Ленина, д. 135А', 'Адлер, Авиационная 34/3', 'г Сочи, р-н Адлерский, ул Авиационная, д. 23', 'Адлер г Авиационная 3/1Г', 'Адлер п., Станиславского ул., 1', 'Адлер, ул.Веселая 86/1', 'г.Адлер, п. Веселое, ул Мира 163 а', 'г.Адлер, ул.Насыпная 81 А', 'Адлер, Ленина 164', 'Адлер пос., Гастелло ул., 40А', 'Сочи, Кипарисовая ул., 4', 'Сочи , Виноградная ул, 272', 'Детляжка, Часовая ул, 11Б', 'Лазаревское пос. ул. Калараша № 151', 'Лазаревское , ул. Калараша, д. 172', 'Лазаревское пос., Лазарева ул., 80б', 'Туапсе г, ул. Богдана Хмельницкого, д. 16 Г', 'Агой с, Ценральный пер., дом № 6', 'г Сочи, ул.Гагарина, д. 67 А', 'Сочи г,ул. Краснодонская 71', 'Сочи, Пластунская ул, 153', 'г Сочи, ул Пластунская, д. 50/1', 'г.Сочи, ул.Пластунская 52ж/6', 'Сочи г,Транспортная ул, 130', 'Сочи г., Раздольное с., Тепличная ул., 20', 'Сочи г, ул. Транспортная № 67', 'Сочи, Голенева ул,, дом 17/2', 'Сочи г, Голенева 28а павильон 88.', 'Сочи г, ул. Транспортная № 5', 'г Сочи, ул Гагарина, д. 76/4', 'Сочи, Лавровая ул, 5', 'Сочи, переулок Теневой, 1/5', 'г Сочи, ул Анапская, д. 1', 'Сочи, ул. Донская,7', 'Туапсе, Маяковского ул,18', 'Новомихайловский п. ул. Мира № 1/8', 'Туапсинский р-н, п.Лермонтово, ул. Новороссийское ш. 3Б', 'Сальск г., Трактовая ул., 25', 'Сальск г., Трактовая ул., 17', 'Сальск г., Кирова ул., 53', 'Белая Глина с., Ленинская ул, 126', 'Белая Глина с., Кооперативная ул., 84 а', 'Новопокровская ст., Ленина ул., 35', 'Тихорецк г., Ачкасова ул., 123 (авторынок)', 'Тихорецк г., Ачкасова ул., 92 (авторынок)', 'Тихорецк г., Ачкасова ул., 94 (авторынок)', 'Тихорецк г., Краснооктябрьская ул., 42/6', 'Тихорецк г., Чапаева ул., 2/5, ГСК Лада', 'Выселки ст., Якименко пер., 4Б', 'Кореновск г., Попова ул., 10', 'Пластуновская ст., Ростовское шоссе ул., 1301 км.+700, Шиномонтаж рядом с Роснефтью', 'Пластуновская ст., Базарная ул., 138', 'Миллерово г, Красная ул, д. 33', 'Каменск-Шахтинский, Лиховская ул, д.16', 'Белая Калитва, ул.Энтузиастов, 5А', 'Новошахтинск г, Украинская ул, дом 44', 'Шахты, ул. Маяковского, 221', 'Шахты, пр. Победа Революции, д. 117', 'Шахты, Комиссаровский переулок 103 а', 'Шахты, ул. Советская, 105', 'Шахты, ул. Шишкина, д.116', 'Новочеркасск, ул. Харьковское шоссе 32а', 'Таганрог с. Николаевка, Ленина, дом № 317Б', 'Таганрог, Николаевское шоссе, 23', 'Таганрог, ул Чехова, д. 283', 'Таганрог, Поляковское шоссе, 12', 'Таганрог, ул Чехова, д. 211', 'Таганрог г, ул. Пальмиро Тольятти, дом 20', 'Таганрог, ул Плотникова, д. 87/1', 'Чалтырь, ул. Ростовская 74', 'Ростов, ул. Шаповалова, 6', 'Ростов, ул. Доватора д. 34А', 'Батайск, ш Самарское, д. 8', 'Батайск, Энгельса 74А/62', 'Ростов, ул Доватора, д. 11', 'Ростов, ул.Доватора, д.146 Л', 'Ростов-на-Дону ул. Доватора, д.146/12', 'Ростов-на-Дону г, Доватора ул, дом 158Д', 'Ростов, Доватора 158/5', 'Ростов г, Доватора ул, 223', 'Азов г, Коллонтаевский пер, дом 82', 'Павловская ст., Ленина ул., № 4а', 'Павловская ст., Промышленная ул., № 18А', 'Павловская ст., Октябрьская ул., 456', 'Ростов, рынок Алмаз, ряд 24, пав.5', 'Ростов, ул. Днепропетровская 54', 'Ростов-на-Дону, ул Вятская, д. 120А', 'Ростов, ул. Геологическая 13', 'Ростов-на-Дону г., пр-т Шолохова, д. 81а', 'Ростов , ул. Нансена 156а', 'Ростов, Нансена 85', 'Ростов-на-Дону г., Королёва пр., 5/2', 'Ростов, 60К-9, 1-й километр, 1', 'Ростов г., Ленинаван х., Пушкинская ул., 1', 'Ростов, ул. Малиновского 33/89, пав 181', 'г. Ростов-на-Дону, ул. Малиновская 15г/2а', 'Ростов, ул. Стачки 70', 'Кущевская ст., Дзержинского ул., 105', 'Крыловская ст., Жлобы ул., № 1', 'Крыловская ст., Красноармейская ул., 32', 'Кущевская ст., Кубанский пер., 47А', 'Кущевская ст., Российская ул., 1А', 'Ленинградская ст., Староминская ул., 20', 'Ленинградская ст., Ленинский пер., 99', 'Ленинградская ст., Жлобы ул., 19', 'Новопластуновская, ул. Советская, 29', 'Кореновск г., К.Маркса ул., 318В', 'Кореновск г., Гагарина ул., 11', 'Кореновск г., Красная ул., № 3, корпус Б', 'Платнировская ст., К. Маркса, 1 "Автодопинг"', 'Мелитополь, ул. Екатерины Великой, д. 184', 'Краснодар г., Ессентукская ул., № 8', 'Краснодар г., Бершанской ул., 349 б', 'Краснодар г., Восточный обход ул., 6', 'Краснодар, ул. Уральская 151/1', 'Краснодар, Сормовская улица, д. 108/3, 4 подъезд , 42 домофон, 4 этаж, кв. 42', 'Краснодар, жилой массив Пашковский, улица Фадеева, д. 429/1, 3 подъезд , 225 домофон, 11 этаж, кв. 225', 'Краснодар г., Знаменский пос., Короткий пер., 16', 'Краснодар г., пос.Знаменский ул. Березовая 35', 'Краснодар г., Зеленопольский пос., Южная ул., 3', 'Краснодар г., Ростовское шоссе ул., 17 километр "РУСШИНА"', 'Динская ст., Крайняя 10А', 'Динская ст., Кирова 108', 'Динская ст., Коммунальная ул., 87 А', 'Динская ст., Садовая ул., 20А', 'Динская ст., Труд Ягодная днт ул, 134', 'Краснодар г., Знаменский пос., Богатырская ул., 15', 'Новая Адыгея а., Тургеневское шоссе ул., 24/1 "Черри"', 'Краснодар, Алма-Атинская улица, д. 50', 'Краснодар г., Северная ул., 209', 'Краснодар г., Бабушкина ул., 109', 'Краснодар г., Аэродромная ул., 56', 'Краснодар г., Красных Партизан ул., 365', 'Краснодар г., Красных Партизан ул., 247', 'Краснодар г., Красных Партизан ул., 74', 'Краснодар г., Ковалева ул., 1/1', 'Краснодар г., Дзержинского ул., 163', 'Краснодар г., Дзержинского ул., 98А', 'Краснодар г., Прохладная ул., 86', 'Краснодар г., проезд 6-й Кореновский, 10', 'Краснодар г., Средняя ул., 20/2', 'Березовый, Карла Гусника ул., 17', 'Краснодар г., Грушевая ул., 9', 'Краснодар г., Российская ул., 536', 'г.Краснодар, Автомобильная, 5', 'Краснодар г., Ростовское Шоссе ул., 26/2 "Черри"', 'Краснодар г., Ростовское Шоссе ул., 23/1, объект 8', 'Краснодар г., Ростовское Шоссе ул., 12, кор. 14', 'Краснодар г., Российская ул., 103/1', 'Краснодар г., Черкасская ул., 26/1', 'Краснодар г., Героев Разведчиков ул, 24', 'краснодар коттеджный посёлок Бавария, 3-й Апшеронский проезд, д. 1', 'Краснодар г., Бородинская ул., 160/3', 'Краснодар г., хутор Ленина, 37', 'Краснодар, ул Восточный Обход, д. 14', 'г. Краснодар, Восточный обход, 45.1134; 39.1181', 'Краснодар г., Пебедитель пос., 18', 'Краснодар г., Мачуги ул., 45', 'Краснодар г., Автолюбителей ул.,17', 'Краснодар г., 2-ая Заречная ул., 32 (Серые ворота, бетонная площадка)', 'ПВЗ ЭНЕРГИЯ Краснодар, ул Новороссийская', 'Новорссийская 216/2 ПЭК', 'Краснодар, Новороссийскя ПЭК', 'Краснодар, ул.Шевченко, 166/1', 'Краснодар г., Шевченко ул., 131/2', 'Краснодар г., Обрывная ул., 131', 'Краснодар г., Димитрова ул., 58', 'Краснодар Ул Радио 3 А', 'Краснодар, ул. Суворова, 12, "Автолэнд"', 'Краснодар г., 1-Й Тихорецкий проезд ул., 21', 'Краснодар г., Ялтинская ул., д. 2, литер «В»', 'Краснодар г., Старокубанская ул., 122/11', 'Краснодар, ул.Лизы Чайкиной д. 22.', 'Краснодар г., Новороссийская ул., 210/4', 'г. Краснодар ул. Уральская 98/2', 'Краснодар г., Новороссийская ул., 236 лит Г', 'Краснодар г., Уральская ул., 126/4 Корк', 'Краснодар г., Уральская ул., 134 А', 'Краснодар ул. Симферопольская 30/1 ИП Кравченко Я.А.', 'Краснодар г., Уральская ул., 117/2', 'Краснодар г., Куренная ул., 105/1', 'Республика Адыгея, п.Яблоновский, ул.Индустриальная 4']
geo_locations = [['45.055403', '39.04805'], ['45.052761', '41.898494'], ['43.436208', '39.937831'], ['43.422833', '39.93068'], ['43.439272', '40.022722'], ['43.624039', '39.745286'], ['43.661341', '39.684578'], ['43.905537', '39.335798'], ['44.117725', '39.109261'], ['43.450883', '39.905033'], ['43.430028', '39.935477'], ['43.432896', '39.936025'], ['43.435508', '39.928515'], ['43.423442', '39.931695'], ['43.438172', '39.911178'], ['43.42777', '40.008834'], ['43.437275', '39.9215'], ['43.441615', '39.909588'], ['43.450608', '39.918212'], ['43.513888', '39.861806'], ['43.639842', '39.698744'], ['43.759971', '39.527966'], ['43.918909', '39.347207'], ['43.919597', '39.350405'], ['43.914818', '39.322395'], ['44.105046', '39.086821'], ['44.147034', '39.038563'], ['43.611358', '39.730679'], ['43.644722', '39.753766'], ['43.618962', '39.740085'], ['43.602024', '39.736707'], ['43.603629', '39.739555'], ['43.569766', '39.756039'], ['43.584571', '39.763414'], ['43.602389', '39.75391'], ['43.609263', '39.7426'], ['43.608447', '39.743876'], ['43.607442', '39.741244'], ['43.6097', '39.732458'], ['43.630603', '39.717708'], ['43.641179', '39.701538'], ['43.633931', '39.705293'], ['43.616175', '39.723116'], ['44.107519', '39.081665'], ['44.258299', '38.864398'], ['44.301422', '38.750285'], ['46.468871', '41.495599'], ['46.468524', '41.496624'], ['46.470889', '41.530643'], ['46.072052', '40.865449'], ['46.072233', '40.866599'], ['45.957321', '40.697994'], ['45.855898', '40.156032'], ['45.854667', '40.156337'], ['45.855458', '40.156661'], ['45.8451', '40.098557'], ['45.844736', '40.099016'], ['45.585148', '39.649813'], ['45.466439', '39.404088'], ['45.304356', '39.234172'], ['45.30125', '39.231584'], ['48.928561', '40.375858'], ['48.313684', '40.259446'], ['48.17619', '40.813122'], ['47.765254', '39.947865'], ['47.710619', '40.16409'], ['47.69583', '40.207433'], ['47.702943', '40.220279'], ['47.704374', '40.224313'], ['47.730375', '40.232595'], ['47.482131', '40.103534'], ['47.289697', '38.841626'], ['47.268331', '38.861038'], ['47.222213', '38.885077'], ['47.213877', '38.874684'], ['47.21638', '38.903331'], ['47.249874', '38.915324'], ['47.261574', '38.924307'], ['47.276603', '39.518731'], ['47.251764', '39.647055'], ['47.242974', '39.643255'], ['47.068949', '39.746822'], ['47.148845', '39.747676'], ['47.24498', '39.648187'], ['47.240447', '39.609048'], ['47.2426', '39.603074'], ['47.242246', '39.583679'], ['47.246038', '39.583481'], ['47.237229', '39.618291'], ['47.101303', '39.424677'], ['46.130361', '39.780087'], ['46.127775', '39.777895'], ['46.133783', '39.818059'], ['47.273448', '39.824095'], ['47.291995', '39.804063'], ['47.278266', '39.775748'], ['47.26638', '39.770511'], ['47.246099', '39.770816'], ['47.242759', '39.728748'], ['47.246051', '39.691845'], ['47.294953', '39.697082'], ['47.295674', '39.658257'], ['47.271467', '39.610629'], ['47.234329', '39.612677'], ['47.220481', '39.613099'], ['47.211777', '39.660602'], ['46.570668', '39.657287'], ['46.314957', '39.961484'], ['46.323684', '39.953138'], ['46.550344', '39.616405'], ['46.562837', '39.603523'], ['46.339141', '39.380525'], ['46.324791', '39.38322'], ['46.32018', '39.386849'], ['46.055299', '39.60752'], ['45.472002', '39.427947'], ['45.450262', '39.491099'], ['45.451729', '39.445473'], ['45.401637', '39.414266'], ['46.846914', '35.382025'], ['45.004519', '39.112225'], ['45.036337', '39.135204'], ['45.040801', '39.121074'], ['45.043699', '39.125314'], ['45.031407', '39.093513'], ['45.031451', '39.128305'], ['45.058059', '39.133695'], ['45.05371', '39.146783'], ['45.132961', '39.18189'], ['45.174619', '39.101481'], ['45.230918', '39.19752'], ['45.224691', '39.21864'], ['45.214184', '39.216466'], ['45.20384', '39.23251'], ['45.260071', '39.231054'], ['45.059281', '39.118352'], ['45.010433', '38.933757'], ['45.040095', '38.924298'], ['45.043941', '38.95317'], ['45.050749', '38.950394'], ['45.052322', '38.968791'], ['45.052793', '38.947932'], ['45.05618', '38.931888'], ['45.052672', '38.945633'], ['45.059612', '38.949028'], ['45.087307', '38.976023'], ['45.096788', '38.979679'], ['45.098124', '38.969429'], ['45.097813', '38.954436'], ['45.121673', '38.94239'], ['45.153215', '38.993046'], ['45.127314', '39.011219'], ['45.097647', '39.013761'], ['45.092207', '38.993216'], ['45.094173', '38.99257'], ['45.087294', '38.990036'], ['45.070874', '38.986973'], ['45.073541', '39.015315'], ['45.065221', '39.01942'], ['45.057861', '39.034099'], ['45.083081', '39.04186'], ['45.005532', '39.104976'], ['45.036904', '39.242822'], ['45.03598', '39.129293'], ['45.1134', '39.1181'], ['45.120687', '39.104491'], ['45.012822', '39.072484'], ['45.007177', '39.065944'], ['45.02389', '39.073903'], ['45.0356', '39.0465'], ['45.035343', '39.045139'], ['45.036273', '39.041339'], ['45.025692', '39.008524'], ['45.023297', '39.009108'], ['44.995692', '39.026382'], ['45.007922', '39.023939'], ['45.027451', '39.00096'], ['45.016747', '38.980613'], ['45.042375', '39.04522'], ['45.027406', '39.029059'], ['45.023068', '39.050349'], ['45.033439', '39.058102'], ['45.035789', '39.040531'], ['45.032101', '39.048283'], ['45.036859', '39.06139'], ['45.035642', '39.067884'], ['45.036305', '39.073975'], ['45.033216', '39.088968'], ['45.039891', '39.093028'], ['45.026769', '39.122637'], ['44.987749', '38.957643']]


# Generate example data to fill the db
def generate_example_products():
    products_data = {"products": []}
    for p in range(10):
        product = {
            "name": f"Product {p}",
            "form-factor": "tire",
            "dimensions": [random.randint(180, 210), random.randint(45, 70), random.randint(14, 20)],
        }
        products_data["products"].append(product)
    return products_data

def generate_example_vehicles():
    vehicles_data = {"vehicles": []}
    for v in range(20):
        vehicle = {
            "name": f"Vehicle {v}",
            "category": random.choice(["B", "C"]),
            "dimensions": [random.randint(2, 10), random.randint(2, 4), random.randint(2, 4)],
            "weight-capacity": random.randint(100, 1000),
        }
        vehicles_data["vehicles"].append(vehicle)
    return vehicles_data

def generate_example_orders():
    orders_data = {"orders": []}
    for o in range(190):
        order = {
            "number": f"Order {o}",
            "date": f"2023-05-{random.randint(1, 30)}",
            "delivery-time-start": f"{random.randint(0, 23)}:{random.randint(0, 59)}",
            "delivery-time-end": f"{random.randint(0, 23)}:{random.randint(0, 59)}",
            "client": f"Client {random.randint(1, 100)}",
            "address": addresses[o],
            "comment": "",
            "geo-location": {
                "latitude": geo_locations[o][0],
                "longitude": geo_locations[o][1]
            },
            "delivery-zone": f"Zone {random.randint(1, 10)}",
            "type": random.choice(["B", "C"]),
            "products": [
                {"name": f"Product {p}", "quantity": random.randint(2, 50)}
                for p in range(random.randint(1, 10))
            ],
            "status": 0
        }
        orders_data["orders"].append(order)
    return orders_data


if __name__ == "__main__":
    random.seed(42)
    db_path = Path('..').resolve() / 'database.db'
    db_is_empty = db_init(db_path)

    products = generate_example_products()
    vehicles = generate_example_vehicles()
    orders = generate_example_orders()
    depot_address = {
        "address": addresses[-1],
        "geo-location": {
            "latitude": geo_locations[-1][0],
            "longitude": geo_locations[-1][1]
        },
        "delivery-zone": None
    }

    upsert_products(products["products"])
    upsert_vehicles(vehicles["vehicles"])
    upsert_orders(orders["orders"])
    insert_addresses([depot_address])
    insert_segments_where_lacking(100000)


