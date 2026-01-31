import logging
import sys
from services.email_service import EmailService

# Configure logging to show output in console
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

def main():
    target_email = "takaoisomura@gmail.com"
    print(f"--- Starting Test Email to {target_email} ---")

    # 1. Initialize Service (Gmail Mode)
    # Credentials are autoloaded from .env
    service = EmailService(provider='gmail')

    # 2. Prepare Dummy Content
    sample_title = "Market Rally Continues as Tech Stocks Surge"
    sample_summary = (
        "Global markets saw a significant uptick today driven by positive earnings "
        "reports from major technology companies. Investors are optimistic about "
        "AI-driven growth, though concerns about inflation persist in some sectors. "
        "Top analysts predict a steady bullish trend for the remainder of the quarter."
    )
    
    html_content = service.format_email_content(sample_title, sample_summary)

    # 3. Send Email
    print("Attempting to send...")
    success = service.send_email(target_email, "Test: Morning 5 Digest", html_content)

    if success:
        print("\n[SUCCESS] Test email processed successfully.")
        print(f"Check the file 'email_to_{target_email}.html' in the backend directory to see the result.")
    else:
        print("\n[FAILURE] Test email failed.")

if __name__ == "__main__":
    main()
