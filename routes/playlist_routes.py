import os
from flask import request, jsonify, Blueprint
from flask_jwt_extended import get_jwt_identity, jwt_required
from pymongo import MongoClient
from dotenv import load_dotenv
from models.Playlist import Playlist

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
    user_id = get_jwt_identity()

    if not name:
        return jsonify({"error": "Name is required"}), 400

    result = Playlist.create_playlist(user_id, name, db)
    if result:
        return jsonify({"message": "Playlist created", "playlist_id": result}), 201
    else:
        return jsonify({"error": "Failed to create playlist"}), 500

@play_app.route("/api/playlists/<playlist_id>", methods=["GET"])
@jwt_required()
def get_playlist(playlist_id):
    playlist = Playlist.get_playlist_by_id(playlist_id, db)
    if playlist:
        return jsonify(playlist), 200
    else:
        return jsonify({"error": "Playlist not found"}), 404

@play_app.route('/api/playlists/<playlist_id>/add', methods=['POST'])
@jwt_required()
def add_to_playlist(playlist_id):
    user_id = get_jwt_identity()
    data = request.json
    tmdb_id = data.get('tmdb_id')
    media_type = data.get('media_type')

    if not tmdb_id or not media_type:
        return jsonify({'error': 'Missing required data'}), 400

    success = Playlist.add_to_playlist(playlist_id, user_id, tmdb_id, media_type, api_key, db)
    if success:
        return jsonify({'success': True, 'message': 'Media added to playlist'}), 200
    else:
        return jsonify({'error': 'Failed to add media to playlist'}), 500

@play_app.route('/api/playlists/<playlist_id>/remove', methods=['DELETE'])
@jwt_required()
def remove_from_playlist(playlist_id):
    user_id = get_jwt_identity()
    data = request.json
    tmdb_id = data.get('tmdb_id')
    media_type = data.get('media_type')

    if not tmdb_id or not media_type:
        return jsonify({'error': 'Missing required data'}), 400

    success = Playlist.remove_from_playlist(playlist_id, user_id, tmdb_id, media_type, db)
    print(playlist_id, user_id, tmdb_id, media_type, db)
    if success:
        return jsonify({'success': True, 'message': 'Media removed from playlist'}), 200
    else:
        return jsonify({'error': 'Failed to remove media from playlist'}), 500

@play_app.route('/api/playlists/user/<user_id>', methods=['GET'])
@jwt_required()
def get_user_playlists(user_id):
    playlists = Playlist.get_playlists_by_user(user_id, db)
    return jsonify(playlists), 200

@play_app.route('/api/playlists/<playlist_id>/delete', methods=['DELETE'])
@jwt_required()
def delete_playlist(playlist_id):
    user_id = get_jwt_identity()

    if not playlist_id:
        return jsonify({'error': 'Playlist ID is required'}), 400

    success = Playlist.delete_playlist(playlist_id, user_id, db)
    if success:
        return jsonify({'success': True, 'message': 'Playlist deleted'}), 200
    else:
        return jsonify({'error': 'Failed to delete playlist'}), 500
