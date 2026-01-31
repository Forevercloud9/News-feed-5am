# Morning 5 MVP

**News Aggregation & Daily Summary App**

## Overview
Morning 5 fetches news from various sources, summarizes them using Google Gemini AI, and delivers a daily email digest to users.

## Project Structure
- `frontend/`: Flutter Application (Settings & Preferences)
- `backend/`: Python + Flask Application (Scheduler, Aggregator, Processor, Email)

## Setup & Running

### 1. Backend (Python)
Navigate to `backend/` and install dependencies:
```bash
cd backend
pip install -r requirements.txt
pip install firebase-admin
```

Create a `.env` file in `backend/` with:
```
GMAIL_SENDER=your-email@gmail.com
GMAIL_APP_PASSWORD=your-app-password
GEMINI_API_KEY=your-gemini-api-key
```

Run the scheduler:
```bash
python main_scheduler.py
```
To trigger a digest immediately, visit: `http://localhost:8080/schedule_daily_digest`

### 2. Frontend (Flutter)
Navigate to `frontend/`:
```bash
cd frontend
flutter pub get
flutter run
```
*Note: Make sure your Flutter environment is correctly set up.*

## Configuration
- **Settings**: Use the Flutter app to toggle genres and manage email recipients (requires Firebase setup).
- **Manual Config**: If Firebase is not set up, the backend will default to sending emails to `GMAIL_SENDER`.
