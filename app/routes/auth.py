from flask import Blueprint, request, jsonify
import jwt
import bcrypt
import datetime
import os
from models.player import get_db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not username or not email or not password:
        return jsonify({"error": "All fields required"}), 400

    password_hash = bcrypt.hashpw(
        password.encode('utf-8'),
        bcrypt.gensalt()
    ).decode('utf-8')

    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO players (username, email, password_hash) VALUES (%s, %s, %s) RETURNING id",
            (username, email, password_hash)
        )
        player_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({
            "message": "Player registered successfully!",
            "player_id": player_id
        }), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            "SELECT id, username, password_hash FROM players WHERE email = %s",
            (email,)
        )
        player = cur.fetchone()
        cur.close()
        conn.close()

        if not player:
            return jsonify({"error": "Player not found"}), 404

        if not bcrypt.checkpw(password.encode('utf-8'), player[2].encode('utf-8')):
            return jsonify({"error": "Wrong password"}), 401

        token = jwt.encode({
            "player_id": player[0],
            "username": player[1],
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        }, os.getenv('SECRET_KEY'), algorithm="HS256")

        return jsonify({
            "message": "Login successful!",
            "token": token,
            "username": player[1]
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500