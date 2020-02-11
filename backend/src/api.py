import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)


db_drop_and_create_all()

# ROUTES
@app.route('/drinks', methods=['GET'])
def drinks():
    drinks = Drink.query.all()
    drinks = [drink.short() for drink in drinks]
    return jsonify({
        'success': True,
        'drinks': drinks
    }), 200


@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def drinks_detail(payload):
    try:
        drinks = Drink.query.all()
        drinks = [drink.long() for drink in drinks]
        return jsonify({
            'success': True,
            'drinks': drinks
        }), 200
    except Exception:
        abort(422)


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def post_drinks(payload):
    try:
        req = request.get_json()
        title = req.get('title', None)
        recipe = json.dumps(req.get('recipe', None))
        drink = Drink(
            title=title,
            recipe=recipe
        )
        drink.insert()
        return jsonify({
            "success": True,
            "drinks": [drink.long()]
        }), 200
    except Exception:
        abort(422)


@app.route('/drinks/<id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def patch_drink(payload, id):
    try:
        req = request.get_json()
        drink = Drink.query.filter_by(id=id).first()
        if drink is None:
            abort(404)
        if req.get('title', None) is not None:
            drink.title = req.get('title', None)
        if req.get('recipe', None) is not None:
            drink.recipe = json.dumps(req.get('recipe', None))
        drink.update()
        return jsonify({
            "success": True,
            "drinks": [drink.long()]
        })
    except Exception:
        abort(422)


@app.route('/drinks/<id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(payload, id):
    try:
        drink = Drink.query.filter_by(id=id).one_or_none()
        if drink is None:
            abort(404)
        drink.delete()
        return jsonify({
            "success": True,
            "delete": id
        }), 200
    except Exception:
        abort(422)


# Error Handling
'''
Example error handling for unprocessable entity
'''
@app.errorhandler(AuthError)
def auth_error(auth_error):
    return jsonify({
        "success": False,
        "error": auth_error.status_code,
        "message": auth_error.error['description']
    }), auth_error.status_code


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404


@app.errorhandler(401)
def not_authorized(error):
    return jsonify({
        'success': False,
        'error': 401,
        'message': "Not authorized"
    }), 401


@app.errorhandler(500)
def server_error(error):
    return jsonify({
        "success": False,
        "error": 500,
        "message": "Internal Server Error"
    }), 500


@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": "Bad Request"
    }), 400
