
import os
import bcrypt
import base64
from bson import ObjectId
from dotenv import load_dotenv
from flask import request,jsonify, Blueprint
from flask_jwt_extended import get_jwt_identity, jwt_required
from pymongo import MongoClient
from controller.user_controller import login, create_user_controller, get_user_data
from models.Media import MediaAPI
from models.User import User
from flask import jsonify

load_dotenv()
client = MongoClient(os.getenv("MONGODB_URI"))
db = client.get_database(os.getenv("MONGODB_DBNAME"))
api_key = os.getenv('TMDB_KEY')
main_bp = Blueprint("main_bp", __name__)

@main_bp.route("/api/login", methods=["POST"])
def login_route():
    data = request.get_json()
    if "email" not in data or "password" not in data:
        return jsonify({"message": "Faltando email ou senha!"}), 400
    email = data["email"]
    password = data["password"]
    response, status_code = login(email, password)
    return jsonify(response), status_code

@main_bp.route("/api/cadastro", methods=["POST"])
def create_user_route():
    data = request.get_json()
    
    if not all(key in data for key in ["username", "email", "password" ]):
        return jsonify({"message": "Missing required fields"}), 400
    username = data["username"]
    email = data["email"]
    role = 'user'
    password = data["password"]
    response, status_code = create_user_controller(email, username, role, password)
    print(response)
    return jsonify(response), status_code

@main_bp.route('/api/data_user', methods=['GET'])
@jwt_required()
def data_user_route():
    return get_user_data()
    
@main_bp.route('/api/user_name', methods=['GET'])
@jwt_required()
def get_user_name():
    user_id = get_jwt_identity()
    user = User.get_user_by_id_model(user_id)
    
    if user:
        return jsonify({"user": user.get("username", "Unknown")}), 200
    else:
        return jsonify({"message": "User not found"}), 404

@main_bp.route('/api/user_id', methods=['GET'])
@jwt_required()
def get_user_id():
    user_id = get_jwt_identity()
    user = User.get_user_by_id_model(user_id)
    
    if user:
        user_role = user.get("role", None)
        is_admin = user_role == "admin"  
        return jsonify({
            "userId": str(user["_id"]),
            "role": user_role,
            "isAdmin": is_admin  
        }), 200
    else:
        return jsonify({"message": "User not found"}), 404
    
@main_bp.route('/api/user/get_profile', methods=['GET'])
@jwt_required()
def get_watched_list_by_user():
    try:
        user_id = get_jwt_identity()
        userRequested = User.get_user_by_id_model(user_id)
        username = request.args.get('username')
        user = User.get_user_by_username_model(username)
        
        if user:
            watched_list = user.get("watched", []) 
            if userRequested == user:
                return jsonify({"watched_media": watched_list, "isOwner": True}), 200
            else:
                return jsonify({"watched_media": watched_list, "isOwner": False}), 200
        else:
            return jsonify({"error": "User not found."}), 404
    except Exception as e:
        print(f"Error retrieving watched list: {e}")
        return jsonify({"error": "Failed to retrieve watched list."}), 500

@main_bp.route('/api/user/watched', methods=['GET'])
@jwt_required()
def get_watched_list():
    try:
        user_id = get_jwt_identity()
        user = User.get_user_by_id_model(user_id)
        if user:
            watched_list = user.get("watched", []) 
            return jsonify({"watched_media": watched_list}), 200
        else:
            return jsonify({"error": "User not found."}), 404
    except Exception as e:
        print(f"Error retrieving watched list: {e}")
        return jsonify({"error": "Failed to retrieve watched list."}), 500
    
@main_bp.route('/api/user/watched/<username>', methods=['GET'])
@jwt_required()
def get_user_watched_list(username):
    try:
        user = User.get_user_by_username_model(username)
        if user:
            watched_list = user.get("watched", [])
            return jsonify({"watched_media": watched_list}), 200
        else:
            return jsonify({"error": "User not found."}), 404
    except Exception as e:
        print(f"Error retrieving watched list: {e}")
        return jsonify({"error": "Failed to retrieve watched list."}), 500

@main_bp.route('/api/user/watched', methods=['DELETE'])
@jwt_required() 
def delete_from_watched_list_route():
    try:
        data = request.json
        tmdb_id = data.get('tmdb_id')
        media_type = data.get('media_type')

        if not tmdb_id:
            return jsonify({"error": "Missing 'tmdb_id' parameter"}), 400
        if not media_type:
            return jsonify({"error": "Missing 'media_type' parameter"}), 400

        if User.delete_from_watched_list(tmdb_id, media_type, api_key):
            return jsonify({"message": "Media removed from watched list successfully"}), 200
        else:
            return jsonify({"error": "Failed to remove media from watched list"}), 500
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@main_bp.route('/api/user/watched', methods=['POST'])
@jwt_required() 
def add_watched_list_route():
    try:
        data = request.json
        tmdb_id = data.get('tmdb_id')
        media_type = data.get('media_type')

        if not tmdb_id or not media_type:
            return jsonify({"error": "Missing parameters"}), 400

        if User.add_watched_list(tmdb_id, media_type, api_key):
            return jsonify({"message": "Media added to watched list successfully"}), 200
        else:
            return jsonify({"error": "Failed to add media to watched list"}), 500
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@main_bp.route("/api/user/media/seen", methods=["GET"])
@jwt_required()
def verify_media_seen():
    try:
        user_id = get_jwt_identity()
        media_id = request.args.get("id")
        media_type = request.args.get("type")

        if not media_id or not media_type:
            return jsonify({"error": "Missing parameters 'id' and/or 'type'"}), 400
        user = User.get_user_by_id_model(user_id)

        if user:
            watched_list = user.get("watched", [])
            for media in watched_list:
                if media.get("tmdb_id") == media_id and media.get("media_type") == media_type:
                    return jsonify({"seen": True}), 200

            return jsonify({"seen": False}), 200
        else:
            return jsonify({"error": "User not found."}), 404
    except Exception as e:
        print(f"Error checking if media is watched: {e}")
        return jsonify({"error": "Failed to check if media is watched."}), 500


@main_bp.route("/api/user/profile", methods=["GET"])
@jwt_required()
def view_profile():
    try:
        user_id = get_jwt_identity()
        user = User.get_user_by_id_model(user_id)
        user["_id"] = str(user["_id"])
        
        if user:
            return jsonify(user), 200
        else:
            return jsonify({"error": "User not found"}), 404

    except Exception as e:
        return jsonify({"error": f"Error viewing profile: {str(e)}"}), 500

@main_bp.route("/api/user/profile", methods=["PUT"])
@jwt_required()
def update_profile():
    try:
        user_id = get_jwt_identity()
        user = User.get_user_by_id_model(user_id)

        new_password = request.form.get("new_password")
        username = request.form.get("username")
        new_email = request.form.get("email")

        if new_email != user["email"]:
            emailAlreadyTaken = User.get_user_by_email_model(new_email)
        else:
            emailAlreadyTaken = False
        
        if username == user["username"]:
            usernameAlreadyTaken = False
        else:
            usernameAlreadyTaken = User.get_user_by_username_model(username)

        if usernameAlreadyTaken:
            return jsonify({"error": "Username already taken"}), 400
        if emailAlreadyTaken:
            return jsonify({"error": "Email already used"}), 401
        
        if new_password:
            hashed_password = bcrypt.hashpw(new_password.encode("utf-8"), bcrypt.gensalt())
            user["password"] = hashed_password.decode("utf-8")
            
        if username:
            user["username"] = username
        
        if new_email:
            user["email"] = new_email
        
        db.users.update_one({"_id": ObjectId(user_id)}, {"$set": user})
        return jsonify({"message": "Profile updated successfully"}), 200
        
    except Exception as e:
        return jsonify({"error": f"Error updating profile: {str(e)}"}), 500

@main_bp.route('/api/user/watched_episodes', methods=['POST'])
@jwt_required() 
def add_watched_episodes_route():
    try:
        data = request.json
        series_id = data.get('series_id')
        season_number = data.get('season_number')
        episode_numbers = [data.get('episode_numbers')]
        if not series_id or not season_number or not episode_numbers:
            return jsonify({"error": "Missing parameters"}), 400
        user_id = get_jwt_identity()
        user = User.get_user_by_id_model(user_id)
        if user:
            watched_episodes = user.get("watched_episodes", [])
            series_index = -1
            for i, series in enumerate(watched_episodes):
                if series.get("series_id") == series_id:
                    series_index = i
                    break
            if series_index == -1:
                series_data = {
                    "series_id": series_id,
                    "seasons": [
                        {
                            "season_number": season_number,
                            "episodes": episode_numbers
                        }
                    ]
                }
                watched_episodes.append(series_data)
            else:
                season_index = -1
                for i, season in enumerate(watched_episodes[series_index]["seasons"]):
                    if season.get("season_number") == season_number:
                        season_index = i
                        break
                if season_index == -1:
                    season_data = {
                        "season_number": season_number,
                        "episodes": episode_numbers
                    }
                    watched_episodes[series_index]["seasons"].append(season_data)
                else:
                    watched_episodes[series_index]["seasons"][season_index]["episodes"].extend(episode_numbers)
            db.users.update_one({"_id": ObjectId(user_id)}, {"$set": {"watched_episodes": watched_episodes}})
            return jsonify({"message": "Watched episodes added successfully"}), 200
        else:
            return jsonify({"error": "User not found."}), 404
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@main_bp.route('/api/user/watched_episodes', methods=['DELETE'])
@jwt_required() 
def delete_watched_episodes_route():
    try:
        data = request.json
        series_id = data.get('series_id')
        season_number = data.get('season_number')
        episode_numbers = [data.get('episode_numbers')]
        if not series_id or not season_number or not episode_numbers:
            return jsonify({"error": "Missing parameters"}), 400
        user_id = get_jwt_identity()
        user = User.get_user_by_id_model(user_id)
        if user:
            watched_episodes = user.get("watched_episodes", [])
            series_index = -1
            for i, series in enumerate(watched_episodes):
                if series.get("series_id") == series_id:
                    series_index = i
                    break
            if series_index != -1:
                season_index = -1
                for i, season in enumerate(watched_episodes[series_index]["seasons"]):
                    if season.get("season_number") == season_number:
                        season_index = i
                        break
                if season_index != -1:
                    watched_episodes[series_index]["seasons"][season_index]["episodes"] = list(set(watched_episodes[series_index]["seasons"][season_index]["episodes"]) - set(episode_numbers))
                    db.users.update_one({"_id": ObjectId(user_id)}, {"$set": {"watched_episodes": watched_episodes}})
                    return jsonify({"message": "Watched episodes removed successfully"}), 200
            return jsonify({"error": "Failed to remove watched episodes"}), 500
        else:
            return jsonify({"error": "User not found."}), 404
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500
    
@main_bp.route('/api/user/watched_episodes/<series_id>/<season_number>/<episode_number>', methods=['GET'])
@jwt_required()
def check_episode_watched(series_id, season_number, episode_number):
    try:
        user_id = get_jwt_identity()
        user = User.get_user_by_id_model(user_id)
        
        if user:
            watched_episodes = user.get("watched_episodes", [])
            for series in watched_episodes:
                if int(series.get("series_id")) == int(series_id):
                    for season in series.get("seasons", []):
                        if int(season.get("season_number")) == int(season_number):
                            if int(episode_number) in season.get("episodes", []):
                                return jsonify({"watched": True}), 200
            return jsonify({"watched": False}), 200
        else:
            return jsonify({"message": "User not found"}), 404
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@main_bp.route('/api/user/watched_episodes/<series_id>/<season_number>', methods=['GET'])
@jwt_required()
def get_watched_episodes(series_id, season_number):
    try:
        user_id = get_jwt_identity()
        user = User.get_user_by_id_model(user_id)
        
        if user:
            watched_episodes = user.get("watched_episodes", [])
            for series in watched_episodes:
                if int(series.get("series_id")) == int(series_id):
                    for season in series.get("seasons", []):
                        if int(season.get("season_number")) == int(season_number):
                            return jsonify({"episodes": season.get("episodes", [])}), 200
            return jsonify({"message": "Episodes not found"}), 404
        else:
            return jsonify({"message": "User not found"}), 404
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500