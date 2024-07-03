import bcrypt
import base64
from flask import jsonify, make_response
from flask_jwt_extended import create_access_token, get_jwt_identity
from models.User import User
from bson import ObjectId
from werkzeug.exceptions import BadRequest 
from middleware.all_middleware import verify_email_registered, verify_username_registered, verify_username

def login(email, password):
    user = User.get_user_by_email_model(email)
    if user and bcrypt.checkpw(password.encode(), base64.b64decode(user["password"].encode())):
        token = create_access_token(identity=str(user["_id"]))
        return {"access_token": token}, 200
    if not user:
        return {"message": "User not in database"}, 402
    else:
        return {"message": "Invalid username or password"}, 401

def create_user_controller(email, username, role, password):
    email_registered = verify_email_registered(email)
    username_registered = verify_username_registered(username)
    username_contains_space = verify_username(username)

    if email_registered:
        return({"message": "Email is not available"}, 400)
    if username_registered:
        return({"message": "Username is not available"}, 401)
    if username_contains_space:
        return ({"message": "Username cannot contain spaces"}, 400)
    if "@" not in email:
        return {"message": "Invalid email format"}, 400
    if len(password) < 6:
        return {"message": "Password must be at least 6 characters long"}, 400

    hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    hashed_password_base64 = base64.b64encode(hashed_password).decode()
    user_id = User.create_user_model(email, username.lower(), role, hashed_password_base64)
    token = create_access_token(identity=str(user_id))
    return {"id": user_id, "message": f"User {username} created", "access_token": token}, 201

def get_user_data():
    try:
        user_id = get_jwt_identity()

        if not user_id or not isinstance(user_id, str):
            raise BadRequest("Invalid user ID")

        object_id = ObjectId(user_id)
        user_data = User.get_user_by_id_model(object_id)

        if user_data:
            user_data['_id'] = str(user_data['_id'])
            return jsonify(user_data), 200
        else:
            return jsonify({"message": "User not found"}), 404

    except BadRequest as e:
        return make_response(jsonify({"error": str(e)}), 400)

    except Exception as e:
        return make_response(jsonify({"error": f"Unknown error: {str(e)}"}), 500)