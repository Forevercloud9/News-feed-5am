import os
import datetime
import logging
from flask import Flask, request, render_template, redirect, url_for
from agents.news_aggregator import NewsAggregator
from agents.content_processor import ContentProcessor
from services.email_service import EmailService
from services.firestore_service import FirestoreService
import json

app = Flask(__name__)

# Genre Labels map for UI
GENRE_LABELS = {
    'domestic_business': 'Domestic Business (Japan)',
    'global_business': 'Global Business (Intl)',
    'finance': 'Finance & Markets',
    'global_tech': 'Global Technology',
    'new_tech': 'AI & New Tech',
    'corporate_tracking': 'Corporate Watch (JT/BAT)',
    'entertainment': 'Entertainment',
    'sports': 'Sports (Ohtani, etc.)',
    'science': 'Science & Space',
    'health': 'Health & Wellness',
    'politics': 'Politics (JP)',
    'startups': 'Startups & VC'
}

def load_local_settings():
    """Load settings from local JSON file."""
    try:
        if os.path.exists('user_settings.json'):
            with open('user_settings.json', 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load local settings: {e}")
    return {}

def save_local_settings(data):
    """Save settings to local JSON file."""
    try:
        with open('user_settings.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        logger.error(f"Failed to save local settings: {e}")

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    firestore_service = FirestoreService()
    
    # --- GET REQUEST ---
    if request.method == 'GET':
        # 1. Try Load from Firestore
        users = firestore_service.get_all_users_settings()
        
        # 2. If Firestore empty/failed, try local JSON
        if not users:
            local_data = load_local_settings()
            if local_data:
                # Local format adaptation
                users = [{'preferences': local_data.get('preferences', {}), 'emails': local_data.get('emails', [])}]
        
        # Default empty if nothing exists
        current_data = users[0] if users else {'preferences': {}, 'emails': [os.getenv('GMAIL_SENDER', '')], 'custom_topics': []}
        
        # Format custom topics for textarea (newline separated)
        custom_topics_str = "\n".join(current_data.get('custom_topics', []))

        # Pass data to template
        return render_template('settings.html', 
                               emails=",".join(current_data['emails']),
                               preferences=current_data['preferences'],
                               custom_topics=custom_topics_str,
                               genre_labels=GENRE_LABELS)

    # --- POST REQUEST ---
    if request.method == 'POST':
        try:
            # 1. Parse Form Data
            # 'emails' will be a list of strings thanks to getlist
            email_list = request.form.getlist('emails')
            # Filter empty strings
            email_list = [e.strip() for e in email_list if e.strip()]
            
            selected_genres = request.form.getlist('genres')
            preferences = {key: (key in selected_genres) for key in GENRE_LABELS.keys()}
            
            raw_custom = request.form.get('custom_topics', '')
            custom_topics = [t.strip() for t in raw_custom.split('\n') if t.strip()]

            # 2. Save to Firestore (Simulating 'default_user' write)
            # Note: We need to extend FirestoreService to have a 'save' method for backend usage if we want full sync.
            # For MVP simplicity, let's SAVE LOCALLY as primary for this Web Dashboard concept, 
            # OR we can try to save to Firestore if we add that method.
            # Let's do both: Save Local JSON (Guaranteed) + Try Firestore.
            
            # Save Local
            save_data = {'emails': email_list, 'preferences': preferences, 'custom_topics': custom_topics}
            save_local_settings(save_data)
            
            # Save Firestore (Optional attempt)
            if firestore_service.db:
                try:
                    firestore_service.db.collection('users').document('default_user_web').set({
                        'email_recipients': email_list,
                        'preferences': preferences,
                        'custom_topics': custom_topics,
                        'last_updated': datetime.datetime.now()
                    }, merge=True)
                except Exception as e:
                    logger.warning(f"Failed to sync to Firestore: {e}")

            return render_template('settings.html', 
                                   message="Settings SAVED successfully!", 
                                   status="success",
                                   emails=",".join(email_list),
                                   preferences=preferences,
                                   custom_topics=raw_custom,
                                   genre_labels=GENRE_LABELS)
                                   
        except Exception as e:
            logger.error(f"Error saving settings: {e}")
            return render_template('settings.html', message=f"Error: {e}", status="error", genre_labels=GENRE_LABELS)



# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/schedule_daily_digest', methods=['POST', 'GET'])
def schedule_daily_digest():
    """
    Entry point for Cloud Scheduler.
    This function triggers the daily news aggregation and delivery process.
    Target Schedule: 04:30 JST (Previous day 19:30 UTC)
    """
    try:
        logger.info("Starting Daily Digest Process...")

        firestore_service = FirestoreService()
        # 1. Try to load from Local JSON first (Priority for Web Dashboard changes)
        local_settings = load_local_settings()
        
        if local_settings:
            # Construct user object from local file
            users_settings = [{
                'id': 'local_web_user',
                'preferences': local_settings.get('preferences', {}),
                'emails': local_settings.get('emails', [os.getenv('GMAIL_SENDER')]),
                'custom_topics': local_settings.get('custom_topics', [])
            }]
            logger.info("Loaded settings from Local JSON.")
        else:
            # 2. Fallback to Firestore
            users_settings = firestore_service.get_all_users_settings()
            
            # 3. If no users found in DB, fallback to default env
            if not users_settings:
                logger.info("No users found in Firestore/Local. Using default environment settings.")
                default_sender = os.getenv('GMAIL_SENDER')
                if default_sender:
                    users_settings = [{
                        'id': 'default_env_user',
                        'preferences': {},
                        'emails': [default_sender]
                    }]
                else:
                     return "No users and no default sender configured.", 200

        email_service = EmailService(provider='gmail')
        aggregator = NewsAggregator()
        processor = ContentProcessor()

        for user in users_settings:
            user_id = user['id']
            recipients = user['emails']
            preferences = user['preferences'] # Map of 'genre': bool
            custom_topics = user.get('custom_topics', [])

            if not recipients:
                logger.info(f"Skipping user {user_id}: No recipients.")
                continue

            logger.info(f"Processing for user: {user_id} | Genres: {preferences.keys()} | Custom: {custom_topics}")

            # 1. Determine active genres
            # If preferences is empty or None, fetch all? Or fetch default?
            # Let's say if preferences are provided, filter by value=True
            selected_genres = []
            if preferences:
                selected_genres = [k for k, v in preferences.items() if v is True]
                if not selected_genres and preferences: 
                    # All false? Skip or fetch all? Let's skip to avoid spam if user unchecked all.
                    logger.info(f"User {user_id} has disabled all genres.")
                    continue
            
            # 2. Collect News
            raw_articles = aggregator.collect_news(selected_genres=selected_genres if selected_genres else None, custom_topics=custom_topics)
            
            if not raw_articles:
                logger.info(f"No articles found for user {user_id}.")
                continue

            # 3. Process Content
            processed_content = processor.process(raw_articles)
            
            if not processed_content:
                 continue

            # 4. Create HTML Body
            html_body = "<h1>Morning 5 Daily Digest</h1><hr>"
            for article in processed_content:
                html_body += f"""
                <div style='margin-bottom: 20px; padding: 10px; background-color: #f9f9f9; border-left: 4px solid #3498db;'>
                    <h3 style='margin-top: 0;'><a href="{article['link']}">{article['title']}</a></h3>
                    <p style='color: #555; font-size: 14px;'>Score: <b>{article['score']}/10</b> | Source: {article['source']}</p>
                    <div style='background-color: white; padding: 10px; border-radius: 5px;'>
                        {article['summary'].replace(chr(10), '<br>')}
                    </div>
                </div>
                """
            
            # 5. Send Email
            email_service.send_daily_digest(recipients, html_body)
            logger.info(f"Sent digest to {len(recipients)} recipients for user {user_id}.")

        logger.info("Daily Digest Process Completed Successfully.")
        return "Daily digest sent successfully", 200

    except Exception as e:
        logger.error(f"Error in daily digest process: {str(e)}")
        return f"Error: {str(e)}", 500

if __name__ == '__main__':
    # Local development server
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
