from source2.example_data_load import generate_example_products, generate_example_vehicles, generate_example_orders
from flask import Flask


app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello, World!'


@app.route('/hs/orders/get_archived_orders', methods=['GET'])
def get_archived_orders():
    return {'orders': []}


@app.route('/hs/orders/get_available_orders', methods=['GET'])
def get_available_orders():
    orders = generate_example_orders()
    return orders


@app.route('/hs/products/get_all_products', methods=['GET'])
def get_all_products():
    products = generate_example_products()
    return products


@app.route('/hs/products/get_product/<name>', methods=['GET'])
def get_product(name):
    return {"products": []}


@app.route('/hs/vehicles/get_all_vehicles', methods=['GET'])
def get_all_vehicles():
    vehicles = generate_example_vehicles()
    return vehicles


@app.route('/hs/vehicles/get_vehicle/<name>', methods=['GET'])
def get_vehicle(name):
    return {"vehicles": []}


@app.route('/hs/vehicles/get_available_vehicles', methods=['GET'])
def get_available_vehicles():
    return {"vehicles": []}


@app.route('/hs/vehicles/get_geodata/<date>', methods=['GET'])
def get_geodata(date):
    return {}


if __name__ == '__main__':
    app.run(debug=True, port=5001)
