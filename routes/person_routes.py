import os
import bcrypt
import base64
from bson import ObjectId
from dotenv import load_dotenv
from flask import request,jsonify, Blueprint
from flask_jwt_extended import get_jwt_identity, jwt_required
from pymongo import MongoClient
from controller.person_controller import create_person_controller
from models.Media import MediaAPI
from models.User import User
from flask import jsonify

load_dotenv()
client = MongoClient(os.getenv("MONGODB_URI"))
db = client.get_database(os.getenv("MONGODB_DBNAME"))

api_key = os.getenv('TMDB_KEY')
person_app = Blueprint("Person_app", __name__)

@person_app.route("/api/person", methods=["POST"])
def create_person_route():
    data = request.get_json()
    
    if not all(key in data for key in ["username", "personId" ]):
        return jsonify({"message": "Missing required fields"}), 400
    username = data["username"]
    personId = data["personId"]
    response, status_code = create_person_controller(personId, username)
    return jsonify(response), status_code

@person_app.route("/api/person/<person_id>", methods=["GET"])
def get_person_route(person_id):
    person = db.persons.find_one({"personId": person_id})
    
    if person:
        return jsonify({
            "_id": str(person["_id"]),
            "personId": person["personId"],
            "username": person["username"]  
        }), 200
    else:
        return jsonify({"message": "Person not found"}), 404

@person_app.route("/api/personByUser/<username>", methods=["GET"])
def get_personByUser_route(username):
    person = db.persons.find_one({"username": username})
    if person:
        return jsonify({
            "_id": str(person["_id"]),
            "personId": person["personId"],
            "username": person["username"]  
        }), 200
    else:
        return jsonify({"message": "Person not found"}), 404