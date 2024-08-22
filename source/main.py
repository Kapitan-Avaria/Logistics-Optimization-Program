from database.db_init import db_init
from database.db_queries import upsert_orders, upsert_delivery_zones, upsert_vehicles
from vrp.vrp_wrapper import VRPWrapper
from config import Config

from pathlib import Path
from flask import Flask, render_template, redirect, request


app = Flask(__name__)
vw = VRPWrapper()
cfg = Config()


@app.route('/')
@app.route('/index')
def index():
    status_texts = {
        True: "Успешно",
        False: "Не удалось",
        None: "Не было"
    }
    status_colors = {
        True: "green",
        False: "red",
        None: "gray"
    }
    return render_template(
        "index.html",
        title='Главная',
        orders=vw.orders,
        vehicles=vw.vehicles,
        url_1c=cfg.URL_1C,
        status=status_texts[vw.status_1c],
        color=status_colors[vw.status_1c]
    )


@app.route('/edit_orders')
def edit_orders():
    return render_template(
        "edit_orders.html",
        title='Редактировать заказы',
        orders=vw.orders,
        clients=vw.clients
    )


@app.route('/update_orders', methods=['POST'])
def update_orders():
    orders = dict()
    if request.method == 'POST':
        for k, v in request.form.items():
            if k == 'update_orders':
                continue
            if int(k.split('_')[-1]) not in orders.keys():
                orders[int(k.split('_')[-1])] = dict()
                orders[int(k.split('_')[-1])]["geo-location"] = dict()

            if "number_" in k:
                order_id = int(k.removeprefix('number_'))
                orders[order_id]['number'] = v
            if "address_" in k:
                order_id = int(k.removeprefix('address_'))
                orders[order_id]['address'] = v
            if "delivery_zone_" in k:
                order_id = int(k.removeprefix('delivery_zone_'))
                orders[order_id]['delivery_zone'] = v
            if "latitude_" in k:
                order_id = int(k.removeprefix('latitude_'))
                orders[order_id]['geo-location']['latitude'] = v
            if "longitude_" in k:
                order_id = int(k.removeprefix('longitude_'))
                orders[order_id]['geo-location']['longitude'] = v
            if "date_" in k:
                order_id = int(k.removeprefix('date_'))
                orders[order_id]['date'] = v
            if "delivery_time_start_" in k:
                order_id = int(k.removeprefix('delivery_time_start_'))
                orders[order_id]['delivery_time_start'] = v
            if "delivery_time_end_" in k:
                order_id = int(k.removeprefix('delivery_time_end_'))
                orders[order_id]['delivery_time_end'] = v
    upsert_orders(list(orders.values()))
    vw.load_data_from_db()
    return redirect(request.referrer)


@app.route('/edit_delivery_zones')
def edit_delivery_zones():
    return render_template(
        "edit_delivery_zones.html",
        title='Редактировать зоны доставки',
        delivery_zones=list(vw.delivery_zones.values()),
        depot_address=cfg.DEPOT_ADDRESS
    )


@app.route('/update_delivery_zones', methods=['POST'])
def update_delivery_zones():
    delivery_zones = dict()
    if request.method == 'POST':
        for k, v in request.form.items():
            if k == 'update_delivery_zones':
                continue
            if k.split('_')[-1] not in delivery_zones.keys():
                delivery_zones[int(k.split('_')[-1])] = dict()

            if "name_" in k:
                zone_id = int(k.removeprefix('name_'))
                delivery_zones[zone_id]["name"] = v
            if "type_" in k:
                zone_id = int(k.removeprefix('type_'))
                delivery_zones[zone_id]["type"] = v
    upsert_delivery_zones(list(delivery_zones.values()))
    vw.load_data_from_db()
    return redirect(request.referrer)


@app.route('/edit_vehicles')
def edit_vehicles():
    return render_template(
        "edit_vehicles.html",
        title='Редактировать машины',
        vehicles=vw.vehicles
    )


@app.route('/update_vehicles', methods=['POST'])
def update_vehicles():
    vehicles = dict()
    if request.method == 'POST':
        for k, v in request.form.items():
            if k == 'update_vehicles':
                continue
            if k.split('_')[-1] not in vehicles.keys():
                vehicles[int(k.split('_')[-1])] = dict()

            if "name_" in k:
                vehicle_id = int(k.removeprefix('name_'))
                vehicles[vehicle_id]["name"] = v
            if "category_" in k:
                vehicle_id = int(k.removeprefix('type_'))
                vehicles[vehicle_id]["category"] = v
    upsert_vehicles(list(vehicles.values()))
    vw.load_data_from_db()
    return redirect(request.referrer)


@app.route('/build_routes')
def build_routes():
    iframe = vw.map.get_root()._repr_html_()

    return render_template(
        "build_routes.html",
        title='Построение маршрутов',
        vehicles=vw.vehicles,
        orders=vw.orders,
        clients=vw.clients,
        folium_map=iframe,
        shift_start_b=cfg.DEFAULT_SHIFT_START_B,
        shift_start_c=cfg.DEFAULT_SHIFT_START_C,
        shift_dur_b=cfg.DEFAULT_SHIFT_DURATION_B,
        shift_dur_c=cfg.DEFAULT_SHIFT_DURATION_C,
    )


@app.route('/load_data',  methods=['POST'])
def load_data_from_db():
    if request.method == 'POST':
        if 'url_1c_input' in request.form.keys() and request.form['url_1c_input'] != '':
            cfg.URL_1C = request.form['url_1c_input']
        vw.request_data_from_1c(db_is_empty, cfg.URL_1C)
        vw.load_data_from_db()
    return redirect(request.referrer)


@app.route('/run_vrp', methods=['POST'])
def run_vrp():
    if request.method == 'POST':
        vehicles_ids = []
        orders_ids = []
        for k, v in request.form.items():
            if 'select_vehicle_' in k:
                vehicle_id = int(k.removeprefix('select_vehicle_'))
                if v == 'on':
                    vehicles_ids.append(vehicle_id)
            if 'select_order_' in k:
                order_id = int(k.removeprefix('select_order_'))
                if v == 'on':
                    orders_ids.append(order_id)

        vw.run(vehicles_ids, orders_ids)
    return redirect('/build_routes')


if __name__ == '__main__':
    db_path = Path('..').resolve() / 'database.db'

    # Initialize main clients and wrappers
    db_is_empty = db_init(db_path)
    vw.request_data_from_1c(db_is_empty, cfg.URL_1C)
    vw.load_data_from_db()

    app.run(debug=True, port=5002)
