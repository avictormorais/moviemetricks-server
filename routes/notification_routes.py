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
    
@notification_bp.route('/api/notification/series', methods=['POST'])
@jwt_required()
def create_series_notification():
    user_id = get_jwt_identity()
    serie_id = request.json.get('id')
    
    if serie_id is None:
        return jsonify({"error": "Serie id is required"}), 400
    
    result = Notification.create_or_get_series(serie_id)
    if result is None:
        return jsonify({"error": "Error creating serie"}), 500
    else:
        Notification.add_serie_to_notify(user_id, serie_id)
        return jsonify({"message": "Serie created successfully"}), 201

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
    
@notification_bp.route('/api/notification/series', methods=['DELETE'])
@jwt_required()
def remove_series_notification():
    user_id = get_jwt_identity()
    serie_id = request.json.get('id')
    
    if serie_id is None:
        return jsonify({"error": "Serie id is required"}), 400
    
    result = Notification.remove_serie_to_notify(user_id, serie_id)
    if result is None:
        return jsonify({"error": "Error removing serie"}), 500
    else:
        return jsonify({"message": "Serie removed successfully"}), 200

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
    
@notification_bp.route('/api/notification/series', methods=['GET'])
@jwt_required()
def get_series_notification():
    user_id = get_jwt_identity()
    serie_id = request.args.get('id')
    
    if serie_id is None:
        return jsonify({"error": "Serie id is required"}), 400
    
    result = Notification.get_serie_notification(user_id, serie_id)
    if result is None:
        return jsonify({"notification_enabled": False}), 200
    else:
        return jsonify({"notification_enabled": True}), 200
    
@notification_bp.route('/check_releases', methods=['GET'])
def check_releases():
    try:
        auth_header = request.headers.get('Authorization')
        secret_key = os.getenv('CRON_SECRET')
        if not secret_key or auth_header != f'Bearer {secret_key}':
            return jsonify({"status": "error", "message": "Unauthorized"}), 401
        Notification.notify_users()
        return jsonify({"status": "success", "message": "Release check completed."}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    
@notification_bp.route('/api/notifications', methods=['GET'])
@jwt_required()
def get_user_notifications():
    user_id = get_jwt_identity()
    notification_id = request.args.get('id')
    if notification_id is not None:
        notification = Notification.get_user_notification(user_id, notification_id)
        return jsonify(notification), 200
    else:
        notifications = Notification.get_user_notifications(user_id)
        return jsonify(notifications), 200

@notification_bp.route('/api/notifications', methods=['DELETE'])
@jwt_required()
def delete_user_notifications():
    user_id = get_jwt_identity()
    try:
        notification_id = request.json.get('id') if request.json else None
    except:
        notification_id = None

    if notification_id is not None:
        result = Notification.remove_user_notification(user_id, notification_id)
        if result is None:
            return jsonify({"error": "Error deleting notification"}), 500
        else:
            return jsonify({"message": "Notification deleted successfully"}), 200
    else:
        result = Notification.remove_user_notifications(user_id)
        if result is None:
            return jsonify({"error": "Error deleting notifications"}), 500
        else:
            return jsonify({"message": "Notifications deleted successfully"}), 200