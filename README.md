# Football Tournament Management System

A full-stack Flask application for managing football leagues, teams, fixtures, results, standings, predictions, and AI-assisted match highlight generation.

Built for tournament organizers, sports analysts, and football fans who want a lightweight but feature-rich management platform.

---

## Project Contributors

- Bharath Nayakanti
- Sagar Das

---

## Overview

This project combines:

- tournament and league administration
- team/player management
- fixture scheduling and scoreboard updates
- live leaderboard generation
- IPL-style match prediction using machine learning
- highlight video generation from uploaded match footage

The application uses Flask for the backend, SQLAlchemy for database models, Jinja templates for the UI, and a Python ML stack for prediction and video processing.

---

## Features

### Tournament Management
- create and manage leagues
- add/delete teams and players
- generate fixtures automatically
- update match scores and finish statuses
- view league standings in real time

### Match and Team Details
- detailed team profile pages
- player statistics and squad management
- fixture lineup management
- lineup viewing and statistics screens

### Predictions
- IPL match prediction interface
- model-based probability output for matchup outcomes
- result display page with favorite team and probability breakdown

### Highlight Generation
- upload a match video
- analyze the file for exciting moments
- generate highlight clips
- download and view the final output video

---

## Tech Stack

- Backend: Python, Flask
- Database: SQLite by default, PostgreSQL-ready via environment config
- Frontend: HTML, CSS, JavaScript, Jinja templates
- ML/AI: scikit-learn, pandas, numpy, xgboost, catboost
- Video/audio processing: OpenCV, librosa
- Deployment: Docker + Render

---

## Repository Structure

```text
football-tournament-system/
├── app/
│   ├── highlight_generator/
│   │   ├── audio_processing/
│   │   ├── video_processing/
│   │   ├── __init__.py
│   │   └── process_highlights.py
│   ├── predictors/
│   │   └── IPL/
│   ├── static/
│   ├── templates/
│   ├── __init__.py
│   ├── models.py
│   └── routes.py
├── instance/
├── migrations/
├── Dockerfile
├── .dockerignore
├── config.py
├── requirements.txt
├── run.py
├── backup.sql
├── reset_db.py
├── README.md
├── .gitignore
└── venv/
```

---

## Prerequisites

Before running locally, make sure you have:

- Python 3.10+ recommended
- FFmpeg installed on your machine
- Git

### Install FFmpeg

On macOS:

```bash
brew install ffmpeg
```

On Ubuntu/Debian:

```bash
sudo apt-get update
sudo apt-get install -y ffmpeg
```

---

## Local Setup

### 1. Clone the project

```bash
git clone https://github.com/Bharath-Nayakanti/Football-Tournament-Management-System.git
cd Football-Tournament-Management-System
```

### 2. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate
```

On Windows:

```bash
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set environment variables

Create a `.env` file or export variables in your shell:

```bash
export SECRET_KEY="your-secret-key"
export FLASK_ENV="development"
```

Optional for Postgres:

```bash
export DATABASE_URL="postgresql://user:password@host:5432/dbname"
```

If `DATABASE_URL` is not set, the app falls back to SQLite automatically.

### 5. Run the app

```bash
python run.py
```

Then open:

```text
http://127.0.0.1:5000
```

---

## Docker Deployment

A Dockerfile is included for deployment on Render or other container platforms.

### Docker build locally

```bash
docker build -t football-tournament-system .
docker run -p 10000:10000 --env PORT=10000 football-tournament-system
```

---

## Render Deployment

This project is configured for deployment on Render using Docker.

### Required environment variables

| Key | Value |
| --- | --- |
| `SECRET_KEY` | any long random secret string |
| `FLASK_ENV` | `production` |
| `DATABASE_URL` | optional Postgres connection string |

### Docker settings in Render

- Runtime: Docker
- Dockerfile path: `./Dockerfile`
- Start command: leave default if using the Dockerfile, or use:

```bash
gunicorn run:app --bind 0.0.0.0:$PORT
```

The app is already set to use environment variables and SQLite fallback when no database URL is provided.

---

## Important Notes

- The app is ready for local development and Docker-based deployment.
- SQLite works well for local use and small demos.
- PostgreSQL is recommended for production persistence and longer-term reliability.
- FFmpeg must be available for the highlight generator to work correctly.

---

## Usage Notes

### League management
- create leagues
- generate fixtures
- update scores and standings

### Prediction module
- visit the IPL prediction page
- submit team and venue details
- review the predicted match probabilities

### Highlight generation
- upload a video file
- wait for background processing to complete
- download the generated highlight video

---

## License

This project is for educational and portfolio/demo purposes.

---

## Future Improvements

- upgrade to a full PostgreSQL production database
- improve admin role control and user permissions
- add real-time match updates
- improve highlight detection accuracy with more advanced ML models
- add REST API support for external integrations
