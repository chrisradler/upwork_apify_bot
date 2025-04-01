Upwork AI Job Scraper
An automated tool that scrapes Upwork for AI-related job postings and sends notifications to a Telegram channel.
Overview
This bot periodically scrapes Upwork for the latest AI job opportunities that match specific criteria (hourly rate, client hiring history, location, etc.) and sends them directly to a Telegram chat. It runs on GitHub Actions, so there's no need for a dedicated server.
Features

🔍 Scrapes multiple Upwork search queries focused on AI jobs
💰 Filters for jobs with higher budgets ($1000+) and rates ($35+/hour)
👥 Targets clients with proven hiring history
🌎 Focuses on jobs from Americas and Europe
🔄 Runs automatically every 30 minutes during business hours (Mon-Fri, 9am-7pm EST)
📱 Sends formatted job notifications to Telegram

Requirements

Python 3.13
Apify account with API token
Telegram bot token and chat ID
GitHub account (for running GitHub Actions)

Installation

Fork this repository
Set up the required secrets in your GitHub repository:

APIFY_TOKEN: Your Apify API token
TELEGRAM_BOT_TOKEN: Your Telegram bot token
TELEGRAM_CHAT_ID: The ID of your Telegram chat/channel



Configuration
GitHub Workflow
The scraper runs on a schedule defined in .github/workflows/upwork_scraper.yml:
yamlCopyschedule:
- cron: '*/30 13-23 * * 1-5'  # Run every 30 minutes mon-fri from 9am - 7pm EST
You can adjust this schedule to your preferred frequency and timezone.
Search Queries
The search criteria are defined in scraper.py. Current criteria include:

AI-related jobs (Web Development, Software Development)
Budget range: $1000-$4999, $5000+
Hourly rate: $35+
Client history: 1-9 hires, 10+ hires
Location: Americas, Europe
Contractor tier: Intermediate, Expert
Proposal count: 0-4, 5-9, 10-14
Sorted by: Most recent

You can modify these search parameters in the run_input section of scraper.py.
Usage
Once set up, the scraper will run automatically according to the schedule. You can also trigger it manually from the Actions tab in your GitHub repository.
Job listings will be sent to your configured Telegram chat with the following information:

Job title
Budget/payment type
Brief description
Posting date
Direct link to the job

Troubleshooting
Check the GitHub Actions logs for any errors. Common issues include:

Invalid API tokens
Rate limiting from Upwork
Telegram API errors

License
MIT
Acknowledgments
This project uses Apify for web scraping capabilities.
