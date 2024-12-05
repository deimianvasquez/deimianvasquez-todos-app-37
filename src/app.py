"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)


# Endpoint que crea un user nuevo
@app.route('/users/<string:username>', methods=['POST'])
def add_new_user(username=None):
    user = User()
    user_true = user.query.filter_by(name=username).first()

    if user_true is not None:
        return jsonify({
            "detail": "User already exists."
        }), 400
    
    else:
        user.name = username
        user.gender = "MALE"
        db.session.add(user)

        try:
            db.session.commit()
            return jsonify({
                "id": user.id,
                "name": user.name
            }), 201
        
        except Exception as err:
            return jsonify(err), 500


# Eliminamos un usuario 
@app.route('/users/<string:username>', methods=['DELETE'])
def delete_one_user(username=None):

    user = User.query.filter_by(name=username).first()
    if user is None:
        return jsonify({
                    "detail": f"User {username} doesn't exist."
                }), 400

    else:
        try:
            db.session.delete(user)
            db.session.commit()
            return jsonify([]), 204
        
        except Exception as err:
            return jsonify(err.args), 500


# Trae un usuario con todos sus detalles
@app.route('/users/<string:username>', methods=['GET'])
def get_one_users(username=None):

    user = User.query.filter_by(name=username).one_or_none() # devuelve uno o nada

    if user is None:
        return jsonify({"detail": f"User {username} doesn't exist."})

    return jsonify(user.serialize()), 200



# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)


