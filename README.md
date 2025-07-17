🤝 Project by<br/>
Bharath Nayakanti and Sagar Das<br/>
---

# ⚽ Football Tournament Management System

A comprehensive platform for organizing football tournaments, managing teams and fixtures, tracking live standings, predicting outcomes, and generating video highlights using audio/video processing.

---

## 🚀 Features

- 🏆 **Tournament Management**
  - Team registration and management
  - Fixture generation (round-robin or custom)
  - Result input interface

- 📊 **Live Standings**
  - Automatically updates based on match outcomes
  - Tracks wins, losses, draws, goals scored/conceded

- 🔮 **Match Predictor**
  - Predicts outcomes using pre-trained ML models (UCL, La Liga)
  - Dynamically supports user-generated tournaments

- 🎥 **Highlight Generator**
  - Extracts highlights from full match videos
  - Uses separate `audio_processing` and `video_processing` modules
  - Outputs trimmed highlight reels based on exciting moments

---

## 🛠️ Tech Stack

- **Backend**: Python (Flask)  
- **Frontend**: HTML, CSS, JavaScript (Flask templating)  
- **Database**: SQLite (via Flask-SQLAlchemy)  
- **Machine Learning**: Scikit-learn, Pandas, NumPy  
- **Highlight Generation**: OpenCV, Librosa, MoviePy  

---

## 📁 Project Structure
Football-Tournament-Management-System/<br/>
│<br/>
├── app/<br/>
│   ├── highlight_generator/<br/>
│   │   ├── audio_processing/<br/>
│   │   ├── video_processing/<br/>
│   │   ├── process_highlights.py<br/>
│   │   └── requirements.txt<br/>
│   ├── predictors/<br/>
│   ├── static/<br/>
│   ├── templates/<br/>
│   ├── models.py<br/>
│   └── routes.py<br/>
│
├── instance/<br/>
├── migrations/<br/>
├── .gitignore<br/>
└── README.md<br/>


---

## 🛠️ Setup Instructions

1. **Clone the Repository**

```bash
git clone https://github.com/Apex1208/Football-Tournament-Management-System.git
cd Football-Tournament-Management-System
```

2. **Create a Virtual Environment (Recommended)**
```bash

python -m venv venv
source venv/bin/activate       # On Linux/macOS
venv\Scripts\activate          # On Windows
```

3. **Install Required Dependencies**
```bash
# General requirements
pip install -r requirements.txt

# Highlight-specific dependencies
cd app/highlight_generator
pip install -r requirements.txt

```

4. **Set Up the Database (Flask Migrate)**
```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade

```

5. **Run the Application**
```bash
flask run
```
The app will start at: http://127.0.0.1:5000<br/>
---

## 🎞️How to Use the Highlight Generator

- Input: Full match video (MP4)
- Output: Trimmed highlight video containing the most exciting moments

---


**Run Highlight Generation**
```bash
cd app/highlight_generator
python process_highlights.py --input path/to/full_match.mp4 --output path/to/highlights.mp4
```

You can customize threshold values and detection strategy inside process_highlights.py.<br/>

---

## 📌 Future Enhancements
- Admin dashboard for full control over leagues and teams
- Real-time commentary using NLP
- Live YouTube integration for auto-publishing highlights
- Deep learning-based highlight detection (YOLO, etc.)
