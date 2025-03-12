from flask import Blueprint, render_template, redirect, request, current_app
from source.domain.data_operator import DataOperator
from source.domain.map_drawer_interface import MapDrawer
from source.domain.entities import *

# cfg = Config()


def create_app_blueprint():
    app = Blueprint('app', __name__)
    dataop: DataOperator = current_app.config["DATA_OPERATOR"]
    map_drawer: MapDrawer = current_app.config["MAP_DRAWER"]

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
            "orders": dataop.db.get_orders(),
            "vehicles": dataop.db.get_vehicles(),
            "url_business_api": current_app.config["URL_BUSINESS_API"],
            # "status": status_texts[dataop.status_1c],
            # "color": status_colors[dataop.status_1c]
        }
        return render_template("page_index.html", **context)

    @app.route('/edit_config', methods=['GET', 'POST'])
    def edit_config():
        if request.method == 'GET':
            context = {
                "title": "Настроить конфигурацию",
                "cfg": current_app.config.__dict__,
                # "cfg_loc": cfg.load_dict_loc()
            }
            return render_template("page_edit_config.html", **context)
        elif request.method == 'POST':
            cfg_dict = current_app.config.__dict__
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
                current_app.config[k] = new_v
            # dataop.from_db()
            return redirect(request.referrer)

    @app.route('/edit_orders', methods=['GET', 'POST'])
    def edit_orders():
        if request.method == 'GET':
            context = {
                "title": "Редактировать заказы",
                "orders": dataop.db.get_orders(),
                "clients": dataop.db.get_clients()
            }
            return render_template("page_edit_orders.html", **context)
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
            for o, order in enumerate(orders.values()):
                dataop.db.upsert_order(Order(**{k: orders[o][k] for k in Order.__annotations__.keys()}))
            # upsert_orders(list(orders.values()))
            # vw.load_data_from_db()
            return redirect(request.referrer)

    @app.route('/edit_delivery_zones', methods=['GET', 'POST'])
    def edit_delivery_zones():
        if request.method == 'GET':
            context = {
                "title": "Редактировать зоны доставки",
                "delivery_zones": dataop.db.get_delivery_zones(),
                "depot_address": current_app.config["DEPOT_ADDRESS"]
            }
            return render_template("page_edit_delivery_zones.html", **context)
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
            for z, zone in enumerate(delivery_zones.values()):
                dataop.db.upsert_delivery_zone(
                    DeliveryZone(**{k: delivery_zones[z][k] for k in DeliveryZone.__annotations__.keys()})
                )
            # upsert_delivery_zones(list(delivery_zones.values()))
            # vw.load_data_from_db()
            return redirect(request.referrer)

    @app.route('/edit_vehicles', methods=['GET', 'POST'])
    def edit_vehicles():
        if request.method == 'GET':
            context = {
                "title": "Редактировать машины",
                "vehicles": dataop.db.get_vehicles()
            }
            return render_template("page_edit_vehicles.html", **context)
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
            for v, vehicle in enumerate(vehicles.values()):
                dataop.db.upsert_vehicle(Vehicle(**{k: vehicles[v][k] for k in Vehicle.__annotations__.keys()}))
            # upsert_vehicles(list(vehicles.values()))
            # vw.load_data_from_db()
            return redirect(request.referrer)

    @app.route('/build_routes')
    def build_routes():
        map_drawer.redraw_map()
        iframe = map_drawer.get_map_iframe()

        # print(vw.selected_but_not_delivered)
        # print(vw.delivered_orders)
        return render_template(
            "page_build_routes.html",
            title='Построение маршрутов',
            vehicles=dataop.db.get_vehicles(),
            orders=dataop.db.get_orders(),
            clients=dataop.db.get_clients(),
            delivered_orders=dataop.db.get_orders(status="delivered"),
            selected_orders=dataop.db.get_orders(status="selected"),
            selected_but_not_delivered=dataop.db.get_orders(status="selected_but_not_delivered"),
            folium_map=iframe,
            shift_start_b=current_app.config["DEFAULT_SHIFT_START_B"],
            shift_start_c=current_app.config["DEFAULT_SHIFT_START_C"],
            shift_dur_b=current_app.config["DEFAULT_SHIFT_DURATION_B"],
            shift_dur_c=current_app.config["DEFAULT_SHIFT_DURATION_C"],
        )

    @app.route('/load_data',  methods=['POST'])
    def load_data_from_db():
        if request.method == 'POST':
            if 'url_business_api_input' in request.form.keys() and request.form['url_business_api_input'] != '':
                current_app.config["URL_BUSINESS_API"] = request.form['url_business_api_input']
            dataop.load_data_from_business_to_db()
            # dataop.from_db()
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

            # vw.run(vehicles_ids, orders_ids)
            # vw.export_routes()
            # # Update selected but not delivered orders
            # vw.selected_but_not_delivered = orders_ids.copy()
            # # Remove delivered orders from selected_but_not_delivered
            # vw.selected_but_not_delivered = [order_id for order_id in vw.selected_but_not_delivered if order_id not in vw.delivered_orders]
        return redirect('/build_routes')

    return app
