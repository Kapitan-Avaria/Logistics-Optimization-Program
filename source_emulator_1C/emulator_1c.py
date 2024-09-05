from example_data_load import generate_example_products, generate_example_vehicles, generate_example_orders
from flask import Flask

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello, World!'


@app.route('/get_archived_orders', methods=['GET'])
def get_archived_orders():
    return {'orders': []}


@app.route('/get_available_orders', methods=['GET'])
def get_available_orders():
    orders = generate_example_orders()
    return orders


@app.route('/get_depot/<depot_id>', methods=['GET'])
def get_depot(depot_id):
    res = {
        "address": "Республика Адыгея, п.Яблоновский, ул.Индустриальная 4",
        "geo-location": {
            "latitude": "44.987749",
            "longitude": "38.957643"
        }
    }
    return res


@app.route('/get_all_products', methods=['GET'])
def get_all_products():
    products = generate_example_products()
    return products


@app.route('/get_product/<name>', methods=['GET'])
def get_product_by_name(name):
    return {"products": []}


@app.route('/get_product_by_id/<product_id>', methods=['GET'])
def get_product_by_id(product_id):
    return {"products": []}


@app.route('/get_all_vehicles', methods=['GET'])
def get_all_vehicles():
    vehicles = generate_example_vehicles()
    return vehicles


@app.route('/get_vehicle/<name>', methods=['GET'])
def get_vehicle(name):
    return {"vehicles": []}


@app.route('/get_available_vehicles', methods=['GET'])
def get_available_vehicles():
    return {"vehicles": []}


@app.route('/get_geodata/<date>', methods=['GET'])
def get_geodata(date):
    return {}


if __name__ == '__main__':
    print('App is running!')
    app.run(debug=True, port=5001)
