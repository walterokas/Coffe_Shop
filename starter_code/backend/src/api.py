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

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
db_drop_and_create_all()

# ROUTES

# Test Route
# @app.route("/api/")
# def index():
#     AUTH_URL = "https://dev-walter.us.auth0.com/authorize?audience=Restaurant&response_type=token&client_id=IUGN6vweCC0Tv1SASsBUZyEIWMdilZls&redirect_uri=http://localhost:8000/api/"
#     return "Hello there: {}".format(AUTH_URL)


'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['GET'])
def getDrinks():
    drinks_obj = Drink.query.all()
    drinks = [drink.short() for drink in drinks_obj]
    return jsonify({"success": True, "drinks": drinks, "status_code": 200})


'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail', methods=['GET'])
@requires_auth(permission='get:drinks-detail')
def getDrinkDetail():
    drinks_obj = Drink.query.all()
    drinks = [drink.short() for drink in drinks_obj]
    print("DRINKS-DETAIL: ", drinks)

    return jsonify({"success": True, "drinks": drinks, "status_code": 200})

'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['POST'])
@requires_auth(permission='post:drinks')
def createDrink():
    try:
        req = json.loads(request.data)
        print("NEW DRINK DATA: ", req)
    except:
        abort(404)

    if req.get('title', None) is None and req.get('recipe', None) is None:
        abort(404)
    drink_obj = Drink(title=str(req.get('title', None)), recipe=str(req.get('recipe', None)))
    drink_obj.insert()
    return jsonify({"success": True, "drinks": req.get('title'), "status_code": 200})

'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<id>', methods=['PATCH'])
@requires_auth(permission='patch:drinks')
def updateDrink(id):
    # if payload['permission'] != 'patch:drinks':
    #     abort(401)
    if id is None:
        abort(404)
    drink_obj = Drink.query.filter(Drink.id == id).one_or_none()
    if drink_obj is None:
        abort(404)

    try:
        req = json.loads(request.data)
    except:
        abort(404)

    if req.get('title', None) is not None:
        drink_obj.title = req.get('title', None)
    if req.get('recipe', None) is not None:
        drink_obj.recipe = req.get('recipe', None)
    drink_obj.update()

    return jsonify({"success": True, "update": id, "status_code": 200})

'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<id>', methods=['DELETE'])
@requires_auth(permission='delete:drinks')
def deleteDrink(id):
    if id is None:
        abort(404)
    drink_obj = Drink.query.filter(Drink.id == id).first()
    if drink_obj is None:
        abort(404)
    drink_obj.delete()

    return jsonify({"success": True, "delete": id, "status_code": 200})

# Error Handling
'''
Example error handling for unprocessable entity
'''


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''
@app.errorhandler(404)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "Resource Not Found"
    }), 404

'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''
@app.errorhandler(401)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 401,
        "message": "Authentication Error"
    }), 401


#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

'''
# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port)
'''