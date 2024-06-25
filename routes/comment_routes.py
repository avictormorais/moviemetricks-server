import os
from flask import request, jsonify, Blueprint
from flask_jwt_extended import get_jwt_identity, jwt_required
from pymongo import MongoClient
from models.Comment import Comment
from dotenv import load_dotenv
from models.User import User

load_dotenv()

client = MongoClient(os.getenv("MONGODB_URI"))
db = client.get_database(os.getenv("MONGODB_DBNAME"))

comment_app = Blueprint("Comment_app", __name__)
user_tk = os.getenv('JWT_SECRET_KEY')
api_key = os.getenv('TMDB_KEY')


@comment_app.route("/api/comment", methods=["POST"])
@jwt_required()
def create_comment_route():
    try:
        user_id = get_jwt_identity()
        data = request.json

        username = data.get('username')
        media_id = data.get('media_id')
        media_type = data.get('media_type')
        review = data.get('review')
        is_spoiler = data.get('is_spoiler')
        stars = data.get('stars')
        title = data.get('title')
        userRole = User.get_user_by_id_model(user_id).get('role')

        if not username or not media_id or not media_type or not review or not stars:
            return jsonify({"error": "Missing required attributes"}), 400

        comment_id = Comment.create_comment(user_id, username, media_id, media_type, review, is_spoiler, stars, title, userRole)

        if comment_id:
            return jsonify({"message": "Comment added successfully", "comment_id": str(comment_id)}), 201
        else:
            return jsonify({"error": "Failed to add comment"}), 500
    except Exception as e:
        return jsonify({"error": f"Error processing the request: {str(e)}"}), 500

@comment_app.route("/api/comment/<comment_id>", methods=["PUT"])
@jwt_required()
def update_comment_route(comment_id):
    try:
        data = request.json

        user_id = get_jwt_identity()
        comment = Comment.get_comment(comment_id)
        if comment and (str(comment.get("user_id")) == str(user_id) or User.get_user_by_id_model(user_id).get('role') == "admin"):
            review = data.get('review')
            is_spoiler = data.get('is_spoiler')
            stars = data.get('stars')
            success = Comment.update_comment(comment_id, review, is_spoiler, stars)

            if success:
                return jsonify({"message": "Comment updated successfully"}), 200
            else:
                return jsonify({"error": "Failed to update comment"}), 500
        else:
            return jsonify({"error": "Unauthorized"}), 401
        
    except Exception as e:
        return jsonify({"error": f"Error processing the request: {str(e)}"}), 500

@comment_app.route("/api/comment/<comment_id>", methods=["DELETE"])
@jwt_required()
def delete_comment_route(comment_id):
    try:
        user_id = get_jwt_identity()
        comment = Comment.get_comment(comment_id)
        if comment and (str(comment.get("user_id")) == str(user_id) or User.get_user_by_id_model(user_id).get('role') == "admin"):
            success = Comment.delete_comment(comment_id)
            if success:
                return jsonify({"message": "Comment deleted successfully"}), 200
            else:
                return jsonify({"error": "Failed to delete comment"}), 500
        else:
            return jsonify({"error": "Unauthorized"}), 401
    except Exception as e:
        return jsonify({"error": f"Error processing the request: {str(e)}"}), 500

@comment_app.route("/api/comment/<media_type>/<media_id>", methods=["GET"])
def get_comments_by_media_route(media_type, media_id):
    try:
        comments_collection = db["comment"]
        comments = comments_collection.find({"media_id": media_id, "media_type": media_type})

        comments_list = []
        for comment in comments:
            comment["_id"] = str(comment["_id"])
            comment["user_id"] = str(comment["user_id"])
            comments_list.append(comment)

        return jsonify({"comments": comments_list}), 200
    except Exception as e:
        return jsonify({"error": f"Error retrieving comments: {str(e)}"}), 500

@comment_app.route("/api/comment/user/<username>", methods=["GET"])
def get_user_comments(username):
    try:
        comments_collection = db["comment"]
        comments = comments_collection.find({"username": username}, {"_id": 0})

        comments_list = []
        for comment in comments:
            comment.pop("_id", None)
            comment.pop("user_id", None)
            comments_list.append(comment)

        return jsonify({"comments": comments_list}), 200
    except Exception as e:
        return jsonify({"error": f"Error retrieving user comments: {str(e)}"}), 500