from database.db_init import db_init

from client_1c.http_client_1c import HTTPClient1C
from geocoding.geocoding_wrapper import GeocodingWrapper
from routing.routing_wrapper import RoutingWrapper
from vrp.vrp_wrapper import VRPWrapper
from pathlib import Path

from flask import Flask, render_template


app = Flask(__name__)


@app.route('/')
def index():
    return render_template("index.html")


if __name__ == '__main__':
    app.run(debug=True)

    db_path = Path('..').resolve() / 'database.db'
    url_1c = ''

    # Initialize main clients and wrappers
    # client1c = HTTPClient1C(url_1c)
    # geocoder = GeocodingWrapper()
    # router = RoutingWrapper()
    db_is_empty = db_init(db_path)

    vrp_wrapper = VRPWrapper()




