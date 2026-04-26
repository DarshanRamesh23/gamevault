from flask import Flask, jsonify
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

from routes.auth import auth_bp
app.register_blueprint(auth_bp, url_prefix='/api/v1/auth')

from routes.players import players_bp
app.register_blueprint(players_bp, url_prefix='/api/v1/players')

from routes.matches import matches_bp
app.register_blueprint(matches_bp, url_prefix='/api/v1/matches')

# Create tables on startup
from models.player import create_players_table
with app.app_context():
    try:
        create_players_table()
        print("✅ Players table ready!")
    except Exception as e:
        print(f"DB init error: {e}")

@app.route('/')
def home():
    return jsonify({
        "project": "GameVault",
        "status": "running",
        "version": "1.0.0",
        "endpoints": {
            "auth": "/api/v1/auth",
            "players": "/api/v1/players",
            "matches": "/api/v1/matches",
            "leaderboard": "/api/v1/leaderboard"
        }
    })

@app.route('/health')
def health():
    return jsonify({"status": "healthy"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)