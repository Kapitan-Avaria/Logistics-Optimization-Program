from db_init import db_init
from db_queries import upsert_orders, upsert_delivery_zones, upsert_vehicles
from vrp_wrapper import VRPWrapper
from config import Config

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
    context = {
        "title": "Главная",
        "orders": vw.orders,
        "vehicles": vw.vehicles,
        "url_1c": cfg.URL_1C,
        "status": status_texts[vw.status_1c],
        "color": status_colors[vw.status_1c]
    }
    return render_template("index.html", **context)


@app.route('/edit_config', methods=['GET', 'POST'])
def edit_config():
    if request.method == 'GET':
        context = {
            "title": "Настроить конфигурацию",
            "cfg": cfg.load_dict(),
            "cfg_loc": cfg.load_dict_loc()
        }
        return render_template("edit_config.html", **context)
    elif request.method == 'POST':
        cfg_dict = cfg.load_dict()
        for k, v in cfg_dict.items():
            if type(v) is bool:
                new_v = False
                if request.form.get(k):
                    new_v = True
            elif type(v) is str:
                new_v = request.form.get(k)
            elif type(v) is float:
                new_v = float(request.form.get(k))
            else:
                new_v = request.form.get(k)
            if new_v is None:
                continue
            cfg.__setattr__(k, new_v)
        vw.load_data_from_db()
        return redirect(request.referrer)


@app.route('/edit_orders', methods=['GET', 'POST'])
def edit_orders():
    if request.method == 'GET':
        context = {
            "title": "Редактировать заказы",
            "orders": vw.orders,
            "clients": vw.clients
        }
        return render_template("edit_orders.html", **context)
    elif request.method == 'POST':
        orders = dict()
        for k, v in request.form.items():
            if k == 'edit_orders':
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


@app.route('/edit_delivery_zones', methods=['GET', 'POST'])
def edit_delivery_zones():
    if request.method == 'GET':
        context = {
            "title": "Редактировать зоны доставки",
            "delivery_zones": list(vw.delivery_zones.values()),
            "depot_address": cfg.DEPOT_ADDRESS
        }
        return render_template("edit_delivery_zones.html", **context)
    elif request.method == 'POST':
        delivery_zones = dict()
        for k, v in request.form.items():
            if k == 'edit_delivery_zones':
                continue
            if int(k.split('_')[-1]) not in delivery_zones.keys():
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


@app.route('/edit_vehicles', methods=['GET', 'POST'])
def edit_vehicles():
    if request.method == 'GET':
        context = {
            "title": "Редактировать машины",
            "vehicles": vw.vehicles
        }
        return render_template("edit_vehicles.html", **context)
    elif request.method == 'POST':
        vehicles = dict()
        for k, v in request.form.items():
            if k == 'edit_vehicles':
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
    vw.draw_map()
    iframe = vw.map.get_root()._repr_html_()

    print(vw.selected_but_not_delivered)
    print(vw.delivered_orders)
    return render_template(
        "build_routes.html",
        title='Построение маршрутов',
        vehicles=vw.vehicles,
        orders=vw.orders,
        clients=vw.clients,
        delivered_orders=vw.delivered_orders,
        selected_orders=[o["id"] for o in vw.orders if vw.orders.index(o) in vw.selected_orders],
        selected_but_not_delivered=vw.selected_but_not_delivered,
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
        vw.export_routes()
        # Update selected but not delivered orders
        vw.selected_but_not_delivered = orders_ids.copy()
        # Remove delivered orders from selected_but_not_delivered
        vw.selected_but_not_delivered = [order_id for order_id in vw.selected_but_not_delivered if order_id not in vw.delivered_orders]
    return redirect('/build_routes')


if __name__ == '__main__':
    # Initialize main clients and wrappers
    db_is_empty = db_init()
    vw.request_data_from_1c(db_is_empty, cfg.URL_1C)
    vw.load_data_from_db()

    app.run(debug=True, port=5002)
