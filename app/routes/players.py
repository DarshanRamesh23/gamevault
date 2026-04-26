from flask import Blueprint, request, jsonify
import jwt
import os
from functools import wraps
from models.player import get_db

players_bp = Blueprint('players', __name__)

# ── JWT Protection Middleware ──────────────────────────
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({"error": "Token missing"}), 401
        try:
            token = token.split(" ")[1]  # Bearer <token>
            data = jwt.decode(token, os.getenv('SECRET_KEY'), algorithms=["HS256"])
            request.player_id = data['player_id']
            request.username = data['username']
        except Exception as e:
            return jsonify({"error": "Invalid token"}), 401
        return f(*args, **kwargs)
    return decorated

# ── GET my profile ─────────────────────────────────────
@players_bp.route('/me', methods=['GET'])
@token_required
def get_profile():
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            "SELECT id, username, email, score, created_at FROM players WHERE id = %s",
            (request.player_id,)
        )
        player = cur.fetchone()
        cur.close()
        conn.close()

        if not player:
            return jsonify({"error": "Player not found"}), 404

        return jsonify({
            "id": player[0],
            "username": player[1],
            "email": player[2],
            "score": player[3],
            "member_since": str(player[4])
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ── UPDATE my profile ──────────────────────────────────
@players_bp.route('/me', methods=['PUT'])
@token_required
def update_profile():
    data = request.get_json()
    username = data.get('username')

    if not username:
        return jsonify({"error": "Username required"}), 400

    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            "UPDATE players SET username = %s WHERE id = %s RETURNING id, username",
            (username, request.player_id)
        )
        updated = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()

        return jsonify({
            "message": "Profile updated!",
            "id": updated[0],
            "username": updated[1]
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ── GET leaderboard (top 10 players) ───────────────────
@players_bp.route('/leaderboard', methods=['GET'])
def get_leaderboard():
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            "SELECT username, score FROM players ORDER BY score DESC LIMIT 10"
        )
        players = cur.fetchall()
        cur.close()
        conn.close()

        leaderboard = [
            {"rank": i+1, "username": p[0], "score": p[1]}
            for i, p in enumerate(players)
        ]

        return jsonify({
            "leaderboard": leaderboard,
            "total_players": len(leaderboard)
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ── ADD score to player ────────────────────────────────
@players_bp.route('/me/score', methods=['POST'])
@token_required
def add_score():
    data = request.get_json()
    points = data.get('points', 0)

    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            "UPDATE players SET score = score + %s WHERE id = %s RETURNING username, score",
            (points, request.player_id)
        )
        updated = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()

        return jsonify({
            "message": f"+{points} points added!",
            "username": updated[0],
            "new_score": updated[1]
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500