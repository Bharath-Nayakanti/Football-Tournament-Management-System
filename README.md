# Football Tournament Management System

<div align="center">

![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.0.3-000000?style=for-the-badge&logo=flask&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![Render](https://img.shields.io/badge/Render-Deployment-46E3B7?style=for-the-badge)

</div>

A full-stack football tournament web application for managing leagues, teams, fixtures, results, standings, predictions, and AI-assisted highlight generation.

This project is built for tournament organizers, sports analysts, and football fans who want a lightweight but feature-rich sports management platform.

---

## Project Owner

- Bharath Nayakanti

---

## Overview

The application combines:

- league and tournament administration
- team and player management
- automatic fixture generation
- live standings and score updates
- IPL match prediction using a trained machine learning model
- video highlight generation from uploaded match footage

The backend is built with Flask and SQLAlchemy, while the frontend uses Jinja templates, HTML, CSS, and JavaScript.

---

## Features

### Tournament Management
- create and manage leagues
- add and delete teams and players
- generate fixtures automatically
- update scores and match status
- track standings in real time

### Team and Fixture Details
- detailed team pages
- player statistics and squad management
- lineup creation and viewing
- fixture-specific stats dashboards

### IPL Prediction Module
- dedicated IPL match prediction interface
- probability-based outcome forecasting
- result page showing the predicted favorite and match probabilities

### Highlight Generation
- upload a match video
- process the video for exciting moments
- generate a highlight clip output
- download the final highlight video from the web app

---

## Tech Stack

- Backend: Python, Flask
- Database: SQLite by default, PostgreSQL-ready via environment configuration
- Frontend: HTML, CSS, JavaScript, Jinja templates
- ML/AI: scikit-learn, pandas, numpy, xgboost, catboost (IPL model)
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
├── .dockerignore
├── .gitignore
├── Dockerfile
├── README.md
├── backup.sql
├── config.py
├── requirements.txt
├── reset_db.py
├── run.py
├── venv/
```

---

## Prerequisites

Before running locally, ensure you have:

- Python 3.10+
- FFmpeg installed
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

### 1. Clone the repository

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

### Build locally with Docker

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
| `SECRET_KEY` | a long random secret string |
| `FLASK_ENV` | `production` |
| `DATABASE_URL` | optional Postgres connection string |

### Docker settings in Render

- Runtime: Docker
- Dockerfile path: `./Dockerfile`
- Start command: use the Dockerfile default, or set:

```bash
gunicorn run:app --bind 0.0.0.0:$PORT
```

The app is already configured to use environment variables and will fall back to SQLite when no database URL is provided.

---

## Important Notes

- the project is ready for local development and Docker-based deployment
- SQLite works well for local testing and demo use
- PostgreSQL is recommended for production persistence
- FFmpeg is required for highlight generation to work correctly

---

## Usage Overview

### League management
- create leagues
- generate fixtures
- update scores and standings

### IPL prediction module
- visit the IPL prediction page
- submit match details and venue information
- review predicted probabilities for IPL matchups only

### Highlight generation
- upload a video file
- wait for processing to complete
- download the final generated highlight video

---

## License

This project is intended for educational and portfolio/demo use.

---

## Future Improvements

- move to PostgreSQL for production storage
- add stronger admin/user role management
- improve highlight generation accuracy with more advanced analysis
- expand support for additional leagues and prediction models
- add REST API support for external integrations

- upgrade to a full PostgreSQL production database
- improve admin role control and user permissions
- add real-time match updates
- improve highlight detection accuracy with more advanced ML models
- add REST API support for external integrations
