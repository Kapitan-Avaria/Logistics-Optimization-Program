from database.db_init import db_init
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
    return render_template("index.html",  title='Главная')


@app.route('/build_routes')
def build_routes():
    iframe = vw.map.get_root()._repr_html_()

    return render_template(
        "build_routes.html",
        title='Построение маршрутов',
        vehicles=vw.vehicles,
        orders=vw.orders,
        folium_map=iframe,
        shift_start_b=cfg.DEFAULT_SHIFT_START_B,
        shift_start_c=cfg.DEFAULT_SHIFT_START_C,
        shift_dur_b=cfg.DEFAULT_SHIFT_DURATION_B,
        shift_dur_c=cfg.DEFAULT_SHIFT_DURATION_C,
    )


@app.route('/load_data',  methods=['POST'])
def load_data_from_db():
    if request.method == 'POST':
        vw.request_data_from_1c(db_is_empty, url_1c)
        vw.load_data_from_db()
    return redirect('/build_routes')


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
    url_1c = 'http://127.0.0.1:5001'

    # Initialize main clients and wrappers
    db_is_empty = db_init(db_path)
    vw.request_data_from_1c(db_is_empty, url_1c)
    vw.load_data_from_db()

    app.run(debug=True, port=5002)
