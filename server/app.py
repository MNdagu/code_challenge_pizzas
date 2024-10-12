#!/usr/bin/env python3

from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response, jsonify
from flask_restful import Api, Resource, reqparse
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# app.json.compact = False
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True


migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)


@app.route('/')
def index():
    return '<h1>Code challenge</h1>'

class Restaurants(Resource):
    def get(self):
        restaurants = Restaurant.query.all()
        return jsonify([restaurant.to_dict(only=('id', 'name', 'address')) for restaurant in restaurants], 200)

api.add_resource(Restaurants, '/restaurants')

class RestaurantByID(Resource):
    
    def get(self, id):
        restaurant = Restaurant.query.filter_by(id=id).first()
        if not restaurant:
            return {'error': 'Restaurant not found'}, 404
        
        return jsonify(restaurant.to_dict(), 200)
    
    def delete(self, id):
        restaurant = Restaurant.query.filter_by(id=id).first()
        if not restaurant:
            return {'error': 'Restaurant not found'}, 404
        db.session.delete(restaurant)
        db.session.commit()
        return "", 204

api.add_resource(RestaurantByID, '/restaurants/<int:id>')

class Pizzas(Resource):
    def get(self):
        pizzas = Pizza.query.all()
        return jsonify([pizza.to_dict() for pizza in pizzas], 200)

api.add_resource(Pizzas, '/pizzas')


class CreateRestaurantPizza(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('price', type=int, required=True, help='Price is required and must be an integer')
        parser.add_argument('pizza_id', type=int, required=True, help='Pizza ID is required and must be an integer')
        parser.add_argument('restaurant_id', type=int, required=True, help='Restaurant ID is required and must be an integer')
        args = parser.parse_args()
        
        price = args['price']
        pizza_id = args['pizza_id']
        restaurant_id = args['restaurant_id']

        try:
            pizza = Pizza.query.get(pizza_id)
            restaurant = Restaurant.query.get(restaurant_id)
            if not pizza or not restaurant:
                raise ValueError("Pizza or Restaurant not found")

            new_restaurant_pizza = RestaurantPizza(
                price=price,
                pizza=pizza,
                restaurant=restaurant
            )

            db.session.add(new_restaurant_pizza)
            db.session.commit()

            response_data = new_restaurant_pizza.to_dict()
            return response_data, 201

        except ValueError as e:
            return {"errors": [str(e)]}, 400
        
api.add_resource(CreateRestaurantPizza, '/restaurant_pizzas')

if __name__ == '__main__':
    app.run(port=5555, debug=True)
