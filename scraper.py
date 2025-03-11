from apify_client import ApifyClient
import requests
import json
import time
import os

# Get credentials from environment variables
APIFY_TOKEN = os.environ.get("APIFY_TOKEN", "apify_api_8HOQdb1OhH5OWM85gKTXNGPEkyz6Le4wuWbX")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "7599920800:AAEc3ZJ6GIHRmSJMFw3hUjaHPoqhcDtGTzw")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "-4779022424")
client =  ApifyClient(token=APIFY_TOKEN)

# Rest of your script remains the same

# Function to send message to Telegram
def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    response = requests.post(url, data=payload)
    return response.json()

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
print("Starting Upwork scraper...")
run = client.actor("Cvx9keeu3XbxwYF6J").call(run_input=run_input)
print(f"Scraping complete. Run ID: {run['id']}")

# Fetch and send results to Telegram
job_count = 0
batch_size = 5  # Number of jobs to send in one message
job_batch = []

for item in client.dataset(run["defaultDatasetId"]).iterate_items():
    job_count += 1
    
    # Get skills as a comma-separated list (up to 5 skills)
    skills = []
    for i in range(0, 5):  # Only include up to 5 skills to keep it concise
        skill_key = f"skills/{i}"
        if skill_key in item and item[skill_key]:
            skills.append(item[skill_key])
    skills_text = ", ".join(skills) if skills else "No skills listed"
    
    # Format job details using exact field names from your CSV
    job_details = (
        f"<b>🔹 {item.get('title', 'No title')}</b>\n"
        f"💰 {item.get('budget', 'N/A')} - {item.get('paymentType', '')}\n"
        f"📝 {item.get('shortBio', 'No description')[:2500]}...\n"
        f"🗓️ {item.get('publishedDate', 'N/A')}\n"
        f"🔗 <a href='{item.get('link', '')}'>View Job</a>\n"
    )
    
    job_batch.append(job_details)
    
    # Send in batches to avoid message length limits
    if len(job_batch) >= batch_size:
        try:
            message = f"<b>📋 UPWORK JOB LISTINGS (Batch {job_count//batch_size})</b>\n\n" + "\n\n".join(job_batch)
            send_telegram_message(message)
            print(f"Sent batch {job_count//batch_size}")
        except Exception as e:
            print(f"Error sending message: {str(e)}")
        job_batch = []
        time.sleep(1)  # Avoid hitting Telegram rate limits

# Send any remaining jobs
if job_batch:
    try:
        message = f"<b>📋 UPWORK JOB LISTINGS (Final Batch)</b>\n\n" + "\n\n".join(job_batch)
        send_telegram_message(message)
        print("Sent final batch")
    except Exception as e:
        print(f"Error sending final message: {str(e)}")

# Send summary message
send_telegram_message(f"✅ Scraping complete! Found {job_count} job listings matching your criteria.")