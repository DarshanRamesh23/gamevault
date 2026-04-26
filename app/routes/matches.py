from flask import Blueprint, request, jsonify
from pymongo import MongoClient
import os
import jwt
from functools import wraps
from datetime import datetime

matches_bp = Blueprint('matches', __name__)

def get_mongo():
    client = MongoClient("mongodb://mongo:27017/")
    return client['gamevault']

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({"error": "Token missing"}), 401
        try:
            token = token.split(" ")[1]
            data = jwt.decode(token, os.getenv('SECRET_KEY'), algorithms=["HS256"])
            request.player_id = data['player_id']
            request.username = data['username']
        except:
            return jsonify({"error": "Invalid token"}), 401
        return f(*args, **kwargs)
    return decorated

# ── Create a match ─────────────────────────────────────
@matches_bp.route('/', methods=['POST'])
@token_required
def create_match():
    data = request.get_json()
    db = get_mongo()

    match = {
        "player_id": request.player_id,
        "username": request.username,
        "opponent": data.get('opponent', 'CPU'),
        "result": data.get('result', 'win'),
        "score": data.get('score', 0),
        "game_mode": data.get('game_mode', 'classic'),
        "events": data.get('events', []),
        "played_at": datetime.utcnow()
    }

    result = db.matches.insert_one(match)

    return jsonify({
        "message": "Match recorded!",
        "match_id": str(result.inserted_id)
    }), 201

# ── Get my match history ───────────────────────────────
@matches_bp.route('/history', methods=['GET'])
@token_required
def get_history():
    db = get_mongo()

    matches = list(db.matches.find(
        {"player_id": request.player_id},
        {"_id": 1, "opponent": 1, "result": 1,
         "score": 1, "game_mode": 1, "played_at": 1}
    ).sort("played_at", -1).limit(10))

    for m in matches:
        m["_id"] = str(m["_id"])
        m["played_at"] = str(m["played_at"])

    return jsonify({
        "username": request.username,
        "total_matches": len(matches),
        "matches": matches
    }), 200

# ── Get match stats ────────────────────────────────────
@matches_bp.route('/stats', methods=['GET'])
@token_required
def get_stats():
    db = get_mongo()

    total = db.matches.count_documents({"player_id": request.player_id})
    wins = db.matches.count_documents({"player_id": request.player_id, "result": "win"})
    losses = db.matches.count_documents({"player_id": request.player_id, "result": "loss"})

    return jsonify({
        "username": request.username,
        "total_matches": total,
        "wins": wins,
        "losses": losses,
        "win_rate": f"{round((wins/total)*100)}%" if total > 0 else "0%"
    }), 200