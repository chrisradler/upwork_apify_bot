from apify_client import ApifyClient
import requests
import time
import os
import logging
from dotenv import load_dotenv
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Get credentials from environment variables
APIFY_TOKEN = os.environ.get("APIFY_TOKEN")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
CLAUDE_API_KEY = os.environ.get("CLAUDE_API_KEY")
client = ApifyClient(token=APIFY_TOKEN)

# Dictionary to store proposals
proposals_dict = {}

# Function to generate proposal with Claude
def generate_proposal_with_claude(job_title, job_description, skills_list, budget):
    """
    Generate a job proposal using Claude API based on the job details
    """
    logging.info(f"Generating proposal for: {job_title}")
    
    # Claude API endpoint
    url = "https://api.anthropic.com/v1/messages"
    
    # Construct a prompt that gives Claude context on what to generate
    prompt = f"""
    Job Title: {job_title}
    
    Job Description: {job_description}
    
    Required Skills: {', '.join(skills_list) if skills_list else 'Not specified'}
    
    Budget: {budget}
    
    I am trying to obtain jobs on upwork as a co-founder of tmplogic, which is a custom AI/Automation and software company. I need claude to be able to generate properly structured proposals based off of the job listing that I provide. The first part of the proposal should be a background about tmplogic and some of our general skills. Keep it short and simple. The next part of the proposal is to format a customized sales pitch explaining that we understand how to complete and deliver the project. This response is meant do a couple things, we want to inform the potential client smart routes to take when working on the specified project, and then reassure the potential client that we are a good fit and want to schedule and introductory call about the potential of working on the project togther. this should be a conversational response. It does not have to be very long to get the point across.

    This should look as if a human is writing this, not ai. dont have any crazy formatting. dont mention the timeline, how much money either.

    The response should consists of 3 main paragraphs. The intro about tmplogic and the response to the job listing, and then a closing paragraph that just contains writing about having an introduction call and potentially working on the project together

    The closing paragraph should only have 2-3 sentences.

    it should start off with "Hey!"

    Do not include any names of people. Do not say "wheelhouse". Do not say we have directly done the same project before.

    Let them know that they will have a team of skilled developers on the project.
    """
    
    # Set up request headers and payload for Claude API
    headers = {
        "x-api-key": CLAUDE_API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }
    
    payload = {
        "model": "claude-3-5-sonnet-20240620",
        "max_tokens": 1000,
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }
    
    # Retry settings
    max_retries = 3
    retry_delay = 5  # seconds
    current_retry = 0
    
    while current_retry < max_retries:
        try:
            # Make the API call to Claude
            response = requests.post(url, headers=headers, json=payload)
            response_data = response.json()
            
            # Check for successful response
            if response.status_code == 200 and 'content' in response_data:
                proposal_text = response_data['content'][0]['text']
                logging.info("Successfully generated proposal with Claude")
                return proposal_text
            
            # Check specifically for overloaded error
            elif response_data.get('error', {}).get('type') == 'overloaded_error':
                current_retry += 1
                wait_time = retry_delay * current_retry
                logging.warning(f"Claude API overloaded. Retry {current_retry}/{max_retries} after {wait_time}s")
                time.sleep(wait_time)
                continue
            
            # Other errors - don't retry
            else:
                logging.error(f"Failed to generate proposal: {response_data}")
                return f"Unable to generate proposal due to API error. Please check logs."
                
        except Exception as e:
            logging.error(f"Exception calling Claude API: {str(e)}")
            return f"Error calling Claude API: {str(e)}"
    
    # If we've exhausted all retries
    return "Could not generate proposal after multiple attempts. Claude API may be experiencing high traffic."

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
batch_size = 1  # Process one job at a time
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
    
    # Truncate description for message display but keep full version for Claude
    description = item.get('shortBio', 'No description')
    full_description = description  # Keep the full description for Claude
    if description and len(description) > 250:
        description = description[:247] + "..."
    
    # Format job details using exact field names from your CSV
    if "hour" not in item.get('publishedDate', ''):
        # Generate a proposal using Claude
        proposal = generate_proposal_with_claude(
            job_title=item.get('title', 'No title'),
            job_description=full_description,
            skills_list=skills,
            budget=item.get('budget', 'Not specified')
        )
        
        # Create a shortened preview of the proposal (first 100 characters)
        proposal_preview = proposal[:100] + "..." if len(proposal) > 100 else proposal
        
        # Include job details with proposal preview
        job_details = (
            f"<b>🔹 {item.get('title', 'No title')}</b>\n"
            f"💰 {item.get('budget', 'N/A')} - {item.get('paymentType', '')}\n"
            f"📝 {description}\n"
            f"🗓️ {item.get('publishedDate', 'N/A')}\n"
            f"🔗 <a href='{item.get('link', '')}'>View Job</a>\n\n"
            f"<b>📝 PROPOSAL PREVIEW:</b>\n{proposal}\n\n"
        )
        
        job_batch.append(job_details)
        
        # Send job listing with proposal preview
        if len(job_batch) >= batch_size:
            try:
                message = f"<b>📋 UPWORK JOB LISTING #{job_count}</b>\n\n" + "\n\n".join(job_batch)
                result = send_telegram_message(message)
                if result.get('ok'):
                    logging.info(f"Sent job #{job_count} with proposal preview")
                else:
                    logging.error(f"Failed to send job #{job_count}: {result}")
            except Exception as e:
                logging.error(f"Error sending message: {str(e)}")
            job_batch = []
            time.sleep(2)  # Delay to avoid rate limits
    else:
        message = f"Job was posted more than an hour ago! Skipping..."
        logging.info(message)

# Send any remaining jobs
if job_batch:
    try:
        message = f"<b>📋 UPWORK JOB LISTING (Final)</b>\n\n" + "\n\n".join(job_batch)
        result = send_telegram_message(message)
        if result.get('ok'):
            logging.info("Sent final job details")
        else:
            logging.error(f"Failed to send final job details: {result}")
    except Exception as e:
        logging.error(f"Error sending final job message: {str(e)}")

# Send summary message
send_telegram_message(f"✅ Scraping complete! Found {job_count} job listings matching your criteria. Full proposals have been sent separately.")