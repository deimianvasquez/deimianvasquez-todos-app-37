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
from models import db, User, Todos
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
    # Logica en el endpoint
    # user = User()
    # user_true = user.query.filter_by(name=username).first()

    # if user_true is not None:
    #     return jsonify({
    #         "detail": "User already exists."
    #     }), 400
    
    # else:
    #     user.name = username
    #     user.gender = "MALE"
    #     db.session.add(user)

    #     try:
    #         db.session.commit()
    #         return jsonify({
    #             "id": user.id,
    #             "name": user.name
    #         }), 201
        
    #     except Exception as err:
    #         return jsonify(err), 500

    # logica en el modelo
    try:
        user = User.create(username=username)
        success, message = user 
        print(user)
        if success is None:
            return jsonify(message), 400
        elif success:
            return jsonify({
                "id": message.id,
                "name": message.name
            })
        else:
            return jsonify("error al intentar guardar el usuario"), 400


    except Exception as err:
        return jsonify("explote"), 500


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


@app.route("/users", methods=["GET"])
def get_all_users():
    users = User.query.all()

    print(users)

    return jsonify({
        "users": list(map(lambda item: item.serialize_users(), users))
    })


@app.route("/todos/<string:username>", methods=["POST"])
def add_one_todo(username=None):
    try:
        body = request.json

        user = User.query.filter_by(name=username).one_or_none()
        todos = Todos()

        if body.get("label") is None:
            return jsonify("debes enviarme un label"), 400
        
        if body.get("is_done") is None:
            return jsonify("debes enviarme un is_done"), 400

        todos.label = body["label"]
        todos.is_done = body.get("is_done")
        todos.user_id = user.id
        db.session.add(todos)

        try:
            db.session.commit()
            return jsonify("tarea guardada exitosamente"), 201
        except Exception as err:
            db.session.rollback()
            return jsonify(err.args), 500

    except Exception as err:
        return jsonify(err.args), 500


@app.route("/todos/<int:theid>", methods=["PUT"])
def update_todo(theid=None):

    body = request.json
    todo_edit = Todos.query.get(theid)


    if body.get("label") is None:
        return jsonify("debes enviarme un label"), 400

    if body.get("is_done") is None:
        return jsonify("debes enviarme un is_done"), 400
    
    if todo_edit is None:
        return jsonify({"message":f"no existe una tarea con el id {theid}"}), 404
    else:
        try:
            todo_edit.label = body["label"]
            todo_edit.is_done = body["is_done"]
            
            db.session.commit()
            return jsonify(todo_edit.serialize()), 201

        except Exception as err:
            return jsonify(err.args), 500




    return jsonify("trabajando por usted"), 201


@app.route("/todos/<int:theid>", methods=["DELETE"])
def delete_todo(theid=None):
    todo = Todos.query.get(theid)

    if todo is None:
        return jsonify({"message":f"todo f{theid} does't exists"}), 404
    
    else:
        try:
            db.session.delete(todo)
            db.session.commit()
            return jsonify([]), 204

        except Exception as err:
            return jsonify("Error, intentelo más tarde. Si el error persiste comuniquese con el administrador de la api")


# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)


