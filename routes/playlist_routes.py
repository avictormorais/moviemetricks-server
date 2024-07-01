import os
from flask import request, jsonify, Blueprint
from flask_jwt_extended import get_jwt_identity, jwt_required
from pymongo import MongoClient
from models.Playlist import Playlist
from dotenv import load_dotenv
from models.User import User

load_dotenv()
client = MongoClient(os.getenv("MONGODB_URI"))
db = client.get_database(os.getenv("MONGODB_DBNAME"))
play_app = Blueprint("play_app", __name__)
api_key = os.getenv('TMDB_KEY')

@play_app.route("/api/playlists/create", methods=["POST"])
@jwt_required()
def create_playlist():
    data = request.json
    name = data.get("name")
    playlist_id = data.get("playlistId")

    if not name or not playlist_id:
        return jsonify({"error": "Name and Playlist ID are required"}), 400
    result = Playlist.create_playlist_model(playlist_id, name.lower())
    
    if result:
        return jsonify({"message": "Playlist created", "playlist_id": result}), 201
    else:
        return jsonify({"error": "Failed to create playlist"}), 500
    

@play_app.route("/api/playlists/<playlist_id>", methods=["GET"])
@jwt_required()
def get_playlist(playlist_id):
    playlist = Playlist.get_playlist_by_id_model(playlist_id)
    if playlist:
        return jsonify(playlist), 200
    else:
        return jsonify({"error": "Playlist not found"}), 404

@play_app.route('/api/playlist', methods=['POST'])
@jwt_required()
def add_to_playlist():
    data = request.json
    
    if  'tmdb_id' not in data or 'media_type' not in data:
        return jsonify({'error': 'Missing required data'}), 400
    tmdb_id = data['tmdb_id']
    media_type = data['media_type']
    success = Playlist.add_to_playlist(tmdb_id, media_type,api_key)
    
    if success:
        return jsonify({'success': True, 'message': 'Media added to playlist'}), 200
    else:
        return jsonify({'error': 'Failed to add media to playlist'}), 500
    

@play_app.route('/api/playlist', methods=['DELETE'])
@jwt_required()
def remove_from_playlist():
    data = request.json
    
    if 'tmdb_id' not in data or 'media_type' not in data:
        return jsonify({'error': 'Missing required data'}), 400
    tmdb_id = data['tmdb_id']
    media_type = data['media_type']
    success = Playlist.remove_from_playlist(tmdb_id, media_type)
    
    if success:
        return jsonify({'success': True, 'message': 'Media removed from playlist'}), 200
    else:
        return jsonify({'error': 'Failed to remove media from playlist'}), 500