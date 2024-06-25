
import os
from flask import request,jsonify, Blueprint
from pymongo import MongoClient 
from models.Media import MediaAPI
from flask import jsonify
from dotenv import load_dotenv
load_dotenv()


client = MongoClient(os.getenv("MONGODB_URI"))
db = client.get_database(os.getenv("MONGODB_DBNAME"))

api_key = os.getenv('TMDB_KEY')
media_app = Blueprint("media_app", __name__)

@media_app.route('/api/media/create', methods=['POST'])
def create_media():
    data = request.json
    tmdb_id = data.get('tmdb_id') 
    media_type = data.get('media_type')

    if tmdb_id and media_type:
        
        media_details = MediaAPI.get_media_details(tmdb_id, media_type, api_key)  

        media_id_inserido = MediaAPI.add_media_to_database(media_details, db)

        if media_id_inserido:
            return jsonify({"message": "Media created successfully", "media_id": media_id_inserido}), 201
        else:
            return jsonify({"message": "Failed to create media"}), 500
    else:
        return jsonify({"message": "Missing tmdb_id or media_type parameter"}), 400  

    

@media_app.route("/api/media/get_or_create", methods=["GET"])
def get_or_create_media_route():
    tmdb_id = request.args.get("tmdb_id")
    media_type = request.args.get("media_type")

    if tmdb_id and media_type:
        media_id = MediaAPI.get_or_create_media(tmdb_id, media_type, db, api_key)
        if media_id:
            return jsonify({"media_id": str(media_id)}), 200
        else:
            return jsonify({"error": "Failed to get or create media."}), 500
    else:
        return jsonify({"error": "Invalid request parameters."}), 400

    
@media_app.route("/api/media", methods=["GET"])
def get_all_media_route():
    all_media = MediaAPI.get_all_media(db)
    return jsonify({"media": all_media}), 200
