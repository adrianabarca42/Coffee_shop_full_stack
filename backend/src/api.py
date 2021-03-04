import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS
from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth
import ssl

ssl._create_default_https_context = ssl._create_unverified_context
app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
# db_drop_and_create_all()

## ROUTES
@app.route('/drinks', methods=['GET'])
@requires_auth('get:drinks')
def get_drinks(payload):
    if not request.method == 'GET':
        abort(405)
    drinks = Drink.query.all()
    short_drinks = []
    for drink in drinks:
        short_drinks.append(drink.short())
    if len(short_drinks) == 0:
        abort(404)
    try:
        return jsonify({
            "success": True,
            "drinks": short_drinks,
        }), 200
    except:
        abort(422)

@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drinks_detail(payload):
    if not request.method == 'GET':
        abort(405)
    drinks = Drink.query.all()
    if len(drinks) == 0:
        abort(404)
    try:
        return jsonify({
            "success": True,
            "drinks": [drink.long() for drink in drinks]
        }), 200
    except:
        abort(422)

@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def post_drinks(payload):
    if not request.method == 'POST':
        abort(405)
    body = request.get_json()
    new_title = body.get('title')
    new_recipe = body.get('recipe')
    newDrink = Drink(title=new_title, recipe=json.dumps(new_recipe))
    newDrink.insert()
    try:
        return jsonify({
            "success": True,
            "drinks": newDrink.long()
        }), 200
    except:
        abort(422)

@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def patch_drinks(payload, id):
    if not request.method == 'PATCH':
        abort(405)
    drink = Drink.query.filter(Drink.id == id).one_or_none()
    if drink is None:
        abort(404)
    body = request.get_json()
    new_title = body.get('title')
    new_recipe = body.get('recipe')
    drink.title = new_title
    drink.recipe = json.dumps(new_recipe)
    drink.update()
    try:
        return jsonify({
            "success": True,
            "drinks": [drink.long()]
        }), 200
    except:
        abort(422)

@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drinks(payload, id):
    if not request.method == 'DELETE':
        abort(405)
    drink = Drink.query.filter(Drink.id == id).one_or_none()
    if drink is None:
        abort(404)
    try:
        drink.delete()
        return jsonify({
            "success": True,
            "delete": drink.id
        }), 200
    except:
        abort(422)

## Error Handling

@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
                "success": False, 
                "error": 422,
                "message": "unprocessable"
                }), 422

@app.errorhandler(404)
def resource_not_found(error):
    return jsonify({
                "success": False, 
                "error": 404,
                "message": "resource not found"
                }), 404

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
                "success": False, 
                "error": 405,
                "message": "method not allowed"
                }), 405

@app.errorhandler(AuthError)
def auth_error(ex):
    return jsonify({
                "success": False,
                "error": ex.status_code,
                "message": ex.error['code']
                }),  ex.status_code
