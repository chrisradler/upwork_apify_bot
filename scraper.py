from apify_client import ApifyClient
import requests
import json
import time
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Get credentials from environment variables
APIFY_TOKEN = os.environ.get("APIFY_TOKEN", "YOUR_APIFY_TOKEN")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "YOUR_TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "YOUR_TELEGRAM_CHAT_ID")
client = ApifyClient(token=APIFY_TOKEN)

# Function to send messages to Telegram
def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    try:
        response = requests.post(url, data=payload)
        result = response.json()
        if not result.get('ok'):
            logging.error(f"Telegram error: {result}")
        return result
    except Exception as e:
        logging.error(f"Exception sending Telegram message: {str(e)}")
        return {"ok": False, "error": str(e)}

# Test Telegram connection
logging.info("Testing Telegram connection...")
test_result = send_telegram_message("🔄 Upwork scraper starting...")
if test_result.get('ok'):
    logging.info("Telegram connection successful")
else:
    logging.error(f"Telegram connection failed: {test_result}")

# Prepare the Actor input with your three URLs
run_input = {
    "startUrls": [
        { "url": "https://www.upwork.com/nx/search/jobs/?amount=1000-4999,5000-&category2_uid=531770282580668419,531770282580668418&client_hires=1-9,10-&contractor_tier=2,3&hourly_rate=35-&location=Americas,Europe&per_page=50&proposals=0-4,5-9,10-14&sort=recency&t=0,1" },
        { "url": "https://www.upwork.com/nx/search/jobs/?amount=1000-4999,5000-&category2_uid=531770282580668419,531770282580668418&client_hires=1-9,10-&contractor_tier=2,3&hourly_rate=35-&location=Americas,Europe&per_page=50&proposals=0-4,5-9,10-14&q=ai&sort=recency&t=0,1" },
        { "url": "https://www.upwork.com/nx/search/jobs/?amount=1000-4999,5000-&category2_uid=531770282580668419,531770282580668418&client_hires=1-9,10-&contractor_tier=2,3&hourly_rate=40-&location=Americas,Europe&per_page=50&proposals=0-4,5-9,10-14&q=ai%20app%20developer&sort=recency&t=0,1" }
    ],
    "removeDuplicates": True,
    "filterLast24Hours": True,
    "proxyCountryCode": "US",
}

# Run the Actor and wait for it to finish
logging.info("Starting Upwork scraper...")
run = client.actor("Cvx9keeu3XbxwYF6J").call(run_input=run_input)
logging.info(f"Scraping complete. Run ID: {run['id']}")

# Fetch results
logging.info("Fetching results from Apify...")
items = list(client.dataset(run["defaultDatasetId"]).iterate_items())
logging.info(f"Found {len(items)} items from Apify")

# If no items found, send a notification and exit
if len(items) == 0:
    send_telegram_message("⚠️ Upwork scraper ran but found no new job listings")
    exit(0)

# Send results to Telegram
job_count = 0
batch_size = 2  # Reduced batch size to avoid message length limits
job_batch = []

for item in items:
    job_count += 1
    
    # Get skills as a comma-separated list (up to 3 skills)
    skills = []
    for i in range(0, 3):  # Only include up to 3 skills to keep it concise
        skill_key = f"skills/{i}"
        if skill_key in item and item[skill_key]:
            skills.append(item[skill_key])
    skills_text = ", ".join(skills) if skills else "No skills listed"
    
    # Truncate description to avoid message length issues
    description = item.get('shortBio', 'No description')
    if description and len(description) > 250:
        description = description[:247] + "..."
    
    # Format job details using exact field names from your CSV
    if "hour" not in item.get('publishedDate', ''):
        job_details = (
            f"<b>🔹 {item.get('title', 'No title')}</b>\n"
            f"💰 {item.get('budget', 'N/A')} - {item.get('paymentType', '')}\n"
            f"📝 {description}\n"
            f"🗓️ {item.get('publishedDate', 'N/A')}\n"
            f"🔗 <a href='{item.get('link', '')}'>View Job</a>\n"
        )
        
        job_batch.append(job_details)
    else:
        message = f"Job was posted more than an hour ago! Skipping..."
        logging.info(message)

    
    # Send in smaller batches to avoid message length limits
    if len(job_batch) >= batch_size:
        try:
            message = f"<b>📋 UPWORK JOB LISTINGS (Batch {job_count//batch_size})</b>\n\n" + "\n\n".join(job_batch)
            result = send_telegram_message(message)
            if result.get('ok'):
                logging.info(f"Sent batch {job_count//batch_size}")
            else:
                logging.error(f"Failed to send batch {job_count//batch_size}: {result}")
        except Exception as e:
            logging.error(f"Error sending message: {str(e)}")
        job_batch = []
        time.sleep(2)  # Increased delay to avoid rate limits

# Send any remaining jobs
if job_batch:
    try:
        message = f"<b>📋 UPWORK JOB LISTINGS (Final Batch)</b>\n\n" + "\n\n".join(job_batch)
        result = send_telegram_message(message)
        if result.get('ok'):
            logging.info("Sent final batch")
        else:
            logging.error(f"Failed to send final batch: {result}")
    except Exception as e:
        logging.error(f"Error sending final message: {str(e)}")

# Send summary message
send_telegram_message(f"✅ Scraping complete! Found {job_count} job listings matching your criteria.")