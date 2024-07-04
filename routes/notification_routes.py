import os
from dotenv import load_dotenv
from flask import request,jsonify, Blueprint
from flask_jwt_extended import get_jwt_identity, jwt_required
from pymongo import MongoClient
from flask import jsonify
from models.Notification import Notification

load_dotenv()
client = MongoClient(os.getenv("MONGODB_URI"))
db = client.get_database(os.getenv("MONGODB_DBNAME"))
notification_bp = Blueprint("Notification_app", __name__)

@notification_bp.route('/api/notification/movie', methods=['POST'])
@jwt_required()
def create_notification():
    user_id = get_jwt_identity()
    movie_id = request.json.get('id')
    
    if movie_id is None:
        return jsonify({"error": "Movie id is required"}), 400
    
    result = Notification.create_or_get_movie(movie_id)
    if result is None:
        return jsonify({"error": "Error creating movie"}), 500
    else:
        Notification.add_movie_to_notify(user_id, movie_id)
        return jsonify({"message": "Movie created successfully"}), 201
      
@notification_bp.route('/api/notification/movie', methods=['DELETE'])
@jwt_required()
def remove_notification():
    user_id = get_jwt_identity()
    movie_id = request.json.get('id')
    
    if movie_id is None:
        return jsonify({"error": "Movie id is required"}), 400
    
    result = Notification.remove_movie_to_notify(user_id, movie_id)
    if result is None:
        return jsonify({"error": "Error removing movie"}), 500
    else:
        return jsonify({"message": "Movie removed successfully"}), 200
      
@notification_bp.route('/api/notification/movie', methods=['GET'])
@jwt_required()
def get_notification():
    user_id = get_jwt_identity()
    movie_id = request.args.get('id')
    
    if movie_id is None:
        return jsonify({"error": "Movie id is required"}), 400
    
    result = Notification.get_movie_notification(user_id, movie_id)
    if result is None:
        return jsonify({"notification_enabled": False}), 200
    else:
        return jsonify({"notification_enabled": True}), 200