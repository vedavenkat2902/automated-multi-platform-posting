# Automated Multi-Platform Posting System

A Python-based REST API that accepts a message containing a single call-to-action (CTA) link and publishes it across five third-party platforms: WordPress, Blogger, DEV Community, Telegram, and Discord.

The application uses FastAPI for request handling and validation, with concurrent publishing attempts and independent error handling for each platform.

## Features

- REST API built using FastAPI.
- Request validation using Pydantic.
- Supports messages up to 200 characters.
- Requires exactly one valid HTTP or HTTPS URL in each message.
- Integrates with five third-party platforms.
- Handles publishing attempts concurrently using Python asyncio.
- Handles platform failures independently.
- Returns individual publishing results, including platform name, status, post URL, public accessibility, date, time, and error details.
- Loads credentials and configuration through environment variables.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python 3 | Backend programming |
| FastAPI | REST API framework |
| Uvicorn | ASGI server |
| Pydantic | Request validation |
| HTTPX | Asynchronous HTTP requests |
| Google API Client | Blogger API integration |
| python-dotenv | Environment variable management |
| Pytest | Automated testing |

## Supported Platforms

1. WordPress
2. Blogger
3. DEV Community
4. Telegram
5. Discord

Each platform has its own integration module.

WordPress, Blogger, and DEV Community publish posts publicly. Telegram publishes messages to a configured channel, while Discord publishes messages through a channel webhook.

## Project Structure

```text
automated-posting/
│
├── app/
│   ├── main.py
│   ├── schemas.py
│   ├── config.py
│   │
│   ├── platforms/
│   │   ├── base.py
│   │   ├── wordpress.py
│   │   ├── blogger.py
│   │   ├── devto.py
│   │   ├── telegram.py
│   │   ├── discord.py
│   └── services/
│       └── posting_service.py
│
├── tests/
│   └── test_posting.py
│
├── blogger_auth.py
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```


## Installation and Setup

### 1. Clone the repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd automated-posting
```

### 2. Create a virtual environment

On Windows:

```powershell
py -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root using `.env.example` as a reference.

Configure the following variables:

```env
# WordPress
WORDPRESS_CLIENT_ID=
WORDPRESS_CLIENT_SECRET=
WORDPRESS_SITE_URL=
WORDPRESS_ACCESS_TOKEN=

# Blogger
BLOGGER_BLOG_ID=

# DEV Community
DEVTO_API_KEY=

# Telegram
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=
TELEGRAM_CHANNEL_USERNAME=

# Discord
DISCORD_WEBHOOK_URL=
```

Use valid credentials and grant the required permissions for each platform.

WordPress uses OAuth authorization through the `/wordpress/connect` and `/wordpress/callback` routes.

Blogger requires a Google Cloud project with the Blogger API enabled and OAuth desktop application credentials. Place the downloaded `credentials.json` file in the project root and run:

```bash
py blogger_auth.py
```

This authenticates the Google account and generates `token.json` for subsequent Blogger API requests.

The `.env`, `credentials.json`, and `token.json` files must remain private and must not be committed to GitHub.

## Running the Application

Start the FastAPI server:

```bash
uvicorn app.main:app --host 127.0.0.1 --port 4000 --reload
```

The API will be available at:

`http://localhost:4000`

Interactive API documentation:

`http://localhost:4000/docs`

## API Documentation

### Endpoint

`POST /posting`

### Request Body

```json
{
  "message": "Check out our latest update: https://example.com"
}
```

### Validation Rules

- The message must not be empty.
- The maximum message length is 200 characters.
- Exactly one valid HTTP or HTTPS URL must be included.
- Messages containing multiple URLs or invalid URLs are rejected.

### Response Format

The API returns an overall success indicator and an individual result for each platform.

Illustrative response:

```json
{
  "success": true,
  "results": [
    {
      "platform": "WordPress",
      "status": "success",
      "posted_url": "https://example.wordpress.com/example-post",
      "public_access": true,
      "date": "2026-11-20",
      "time": "10:30:00",
      "error": null
    },
    {
      "platform": "Discord",
      "status": "success",
      "posted_url": null,
      "public_access": null,
      "date": "2026-11-20",
      "time": "10:30:00",
      "error": null
    }
  ]
}
```

The example is illustrative. Actual results depend on platform API responses and configured credentials.

### Overall Success Logic

- `success: true` when at least one platform publishes successfully.
- `success: false` when all platform publishing attempts fail.
- A failure on one platform does not prevent publishing attempts on the others.

## Running Tests

Run the automated test suite:

```bash
pytest -v
```

The test suite covers:

- Valid message submission.
- Missing URL validation.
- Multiple URL validation.
- Maximum message length validation.
- Invalid URL validation.
- Independent platform failure handling.
- Partial success handling.
- Platform publishing calls and response structure.

## Security

- API credentials are loaded through environment variables.
- The `.env` file is excluded from version control.
- Google OAuth credential and token files are excluded from version control.
- `.env.example` provides a configuration template without exposing secrets.
- Platform integrations handle API errors independently.

## Author

**Veda Venkat R**