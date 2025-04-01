# Upwork AI Job Scraper with Proposal Generator

An automated tool that scrapes Upwork for AI-related job postings, generates customized proposals using Claude AI, and sends both to your Telegram channel.

## Overview

This bot periodically scrapes Upwork for the latest AI job opportunities that match specific criteria (hourly rate, client hiring history, location, etc.). For each job found, it uses Claude AI to generate a tailored proposal and sends both the job details and proposal directly to a Telegram chat. It runs on GitHub Actions, so there's no need for a dedicated server.

## Features

- 🔍 Scrapes multiple Upwork search queries focused on AI jobs
- 💰 Filters for jobs with higher budgets ($1000+) and rates ($35+/hour)
- 👥 Targets clients with proven hiring history
- 🌎 Focuses on jobs from Americas and Europe
- 🤖 Automatically generates customized proposals with Claude AI
- 🔄 Runs automatically every 30 minutes during business hours (Mon-Fri, 9am-7pm EST)
- 📱 Sends formatted job notifications and proposals to Telegram

## Requirements

- Python 3.13
- Apify account with API token
- Telegram bot token and chat ID
- Claude API key (Claude 3.5 Sonnet model)
- GitHub account (for running GitHub Actions)
- Apify account
- Apify actor https://console.apify.com/actors/Cvx9keeu3XbxwYF6J/input

## Installation

1. Fork this repository
2. Set up the required secrets in your GitHub repository:
   - `APIFY_TOKEN`: Your Apify API token
   - `TELEGRAM_BOT_TOKEN`: Your Telegram bot token
   - `TELEGRAM_CHAT_ID`: The ID of your Telegram chat/channel
   - `CLAUDE_API_KEY`: Your Anthropic Claude API key

Alternatively, you can use the `.env` file for local development and testing:

```
# Apify credentials
APIFY_TOKEN=YOUR_APIFY_TOKEN

# Telegram bot credentials
TELEGRAM_BOT_TOKEN=YOUR_TELEGRAM_BOT_TOKEN
TELEGRAM_CHAT_ID=YOUR_TELEGRAM_CHAT_ID

# Claude API credentials
CLAUDE_API_KEY=YOUR_CLAUDE_API_KEY

# Optional: Configure proxy if needed
# PROXY_URL=http://user:pass@proxy.example.com:8080

# Optional: Configure runtime settings
MAX_RETRIES=3
RETRY_DELAY=5
BATCH_SIZE=1
```

## Configuration

### GitHub Workflow

The scraper runs on a schedule defined in `.github/workflows/upwork_scraper.yml`:

```yaml
schedule:
- cron: '*/30 13-23 * * 1-5'  # Run every 30 minutes mon-fri from 9am - 7pm EST
```

You can adjust this schedule to your preferred frequency and timezone.

You will need to setup github secrets for the APIFY_TOKEN, TELEGRAM_BOT_TOKEN, and TELGRAM_CHAT_ID.
To do this:
- Access repository
- Navigate to secrets and Variables -> Actions -> New Repository Secrets 

### Search Queries

The search criteria are defined in `scraper.py`. Current criteria include:

- AI-related jobs (Web Development, Software Development)
- Budget range: $1000-$4999, $5000+
- Hourly rate: $35+
- Client history: 1-9 hires, 10+ hires
- Location: Americas, Europe
- Contractor tier: Intermediate, Expert
- Proposal count: 0-4, 5-9, 10-14
- Sorted by: Most recent

You can modify these search parameters in the `run_input` section of `scraper.py`.

### Proposal Customization

The AI-generated proposals are tailored to present your business (tmplogic) as a custom AI/Automation and software company. The proposal template is defined in the `generate_proposal_with_claude` function and includes:

1. An introduction about your company
2. A customized pitch showing understanding of the project
3. A closing paragraph suggesting a call to discuss the project

Modify the prompt in this function to adjust the proposal style and content to match your business.

## Usage

Once set up, the scraper will run automatically according to the schedule. You can also trigger it manually from the Actions tab in your GitHub repository.

For each job listing found, the system will:
1. Scrape the job details from Upwork
2. Generate a customized proposal using Claude AI
3. Send both to your Telegram chat

The message will contain:
- Job title and budget
- Brief description
- Posting date
- Direct link to the job
- Full AI-generated proposal

## Dependencies

- `apify-client`: Interface with Apify web scraping service
- `requests`: HTTP requests for API communication
- `python-dotenv`: Environment variable management

## Troubleshooting

Check the GitHub Actions logs for any errors. Common issues include:

- Invalid API tokens or authentication failures
- Rate limiting from Upwork, Telegram, or Claude APIs
- Proposal generation failures (Claude API overloaded)

The script includes retry logic for API calls to handle temporary service disruptions.

## License

MIT

## Acknowledgments

This project uses:
- [Apify](https://apify.com/) for web scraping capabilities
- [Claude AI](https://www.anthropic.com/claude) for automated proposal generation