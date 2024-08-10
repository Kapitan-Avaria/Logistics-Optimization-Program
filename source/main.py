from database.db_init import db_init

from client_1c.http_client_1c import HTTPClient1C
from geocoding.geocoding_wrapper import GeocodingWrapper
from routing.routing_wrapper import RoutingWrapper
from vrp.vrp_wrapper import VRPWrapper
from pathlib import Path

from flask import Flask, render_template


app = Flask(__name__)


@app.route('/')
@app.route('/index')
def index():
    return render_template("index.html",  title='Главная')


@app.route('/build_routes')
def build_routes():
    return render_template("build_routes.html", title='Построение маршрутов')


if __name__ == '__main__':
    app.run(debug=True)

    db_path = Path('..').resolve() / 'database.db'
    url_1c = ''

    # Initialize main clients and wrappers
    # client1c = HTTPClient1C(url_1c)
    # gw = GeocodingWrapper()
    # rw = RoutingWrapper()
    db_is_empty = db_init(db_path)

    vw = VRPWrapper()
    vw.load_data(db_is_empty, url_1c)




