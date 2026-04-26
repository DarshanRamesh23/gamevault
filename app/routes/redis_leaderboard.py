from flask import Blueprint, request, jsonify
import redis
import jwt
import os
from functools import wraps

redis_lb_bp = Blueprint('redis_leaderboard', __name__)

def get_redis():
    return redis.Redis(host='redis', port=6379, decode_responses=True)

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

# ── Add score to Redis leaderboard ─────────────────────
@redis_lb_bp.route('/add', methods=['POST'])
@token_required
def add_to_leaderboard():
    data = request.get_json()
    points = data.get('points', 0)

    r = get_redis()
    r.zincrby('gamevault:leaderboard', points, request.username)
    new_score = r.zscore('gamevault:leaderboard', request.username)
    rank = r.zrevrank('gamevault:leaderboard', request.username)

    return jsonify({
        "message": f"+{points} points added!",
        "username": request.username,
        "total_score": int(new_score),
        "rank": rank + 1
    }), 200

# ── Get top 10 leaderboard ─────────────────────────────
@redis_lb_bp.route('/top', methods=['GET'])
def get_top():
    r = get_redis()
    top_players = r.zrevrange(
        'gamevault:leaderboard', 0, 9, withscores=True
    )

    leaderboard = [
        {
            "rank": i + 1,
            "username": player[0],
            "score": int(player[1])
        }
        for i, player in enumerate(top_players)
    ]

    return jsonify({
        "leaderboard": leaderboard,
        "powered_by": "Redis sorted sets"
    }), 200

# ── Get my rank ────────────────────────────────────────
@redis_lb_bp.route('/my-rank', methods=['GET'])
@token_required
def my_rank():
    r = get_redis()
    score = r.zscore('gamevault:leaderboard', request.username)
    rank = r.zrevrank('gamevault:leaderboard', request.username)

    if score is None:
        return jsonify({
            "message": "You're not on the leaderboard yet!",
            "tip": "POST to /api/v1/leaderboard/add to join"
        }), 404

    return jsonify({
        "username": request.username,
        "score": int(score),
        "rank": rank + 1
    }), 200