# 🎮 GameVault — Multiplayer Game Backend Platform

![CI](https://github.com/DarshanRamesh23/gamevault/actions/workflows/ci.yml/badge.svg)

A production-grade backend API powering a multiplayer game platform.
Built with Flask, PostgreSQL, MongoDB, Redis, Docker, and GitHub Actions CI/CD.

## 🏗️ Architecture
- **Auth Service** — JWT authentication (Flask + PostgreSQL)
- **Player Profiles** — CRUD with score tracking (PostgreSQL)
- **Match History** — Flexible game event storage (MongoDB)
- **Live Leaderboard** — Real-time rankings with Redis sorted sets
- **Containerised** — Full stack runs with `docker compose up -d`
- **CI/CD** — Auto-build and test on every push

## 🚀 Quick Start
```bash
git clone https://github.com/DarshanRamesh23/gamevault.git
cd gamevault
docker compose up -d
```

## 📡 API Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/v1/auth/register | Register player |
| POST | /api/v1/auth/login | Login + JWT token |
| GET | /api/v1/players/me | Get my profile |
| POST | /api/v1/players/me/score | Add score |
| GET | /api/v1/players/leaderboard | Top players |
| POST | /api/v1/matches/ | Record a match |
| GET | /api/v1/matches/history | Match history |
| GET | /api/v1/matches/stats | Win/loss stats |
| POST | /api/v1/leaderboard/add | Add to Redis leaderboard |
| GET | /api/v1/leaderboard/top | Real-time top 10 |

## 🛠️ Tech Stack
Python · Flask · PostgreSQL · MongoDB · Redis · Docker · JWT · GitHub Actions · AWS EC2

## 👨‍💻 Built by Darshan Ramesh T