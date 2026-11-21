
from pathlib import Path
from urllib.parse import urlencode
import secrets
from app.platforms.blogger import BloggerPlatform
import httpx
from dotenv import set_key
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from app.platforms.devto import DevToPlatform

from app.config import settings
from app.schemas import PostingRequest
from app.services.posting_service import PostingService

from app.platforms.wordpress import WordPressPlatform
from app.platforms.telegram import TelegramPlatform
from app.platforms.discord import DiscordPlatform


# Initialize FastAPI
app = FastAPI(
    title="Automated Multi-Platform Posting System",
    description="Automatically publish messages across multiple platforms.",
    version="1.0.0"
)


# Initialize existing platform integrations
platforms = [
    WordPressPlatform(),
    BloggerPlatform(),
    DevToPlatform(),
    TelegramPlatform(),
    DiscordPlatform()
]


# Initialize posting service
posting_service = PostingService(platforms)


# Required POST endpoint
@app.post("/posting")
async def create_post(request: PostingRequest):

    result = await posting_service.post_message(
        request.message
    )

    return result


# WordPress OAuth configuration
WORDPRESS_REDIRECT_URI = (
    "http://localhost:4000/wordpress/callback"
)

# Temporary state storage for local development
oauth_states = set()


# Step 1: Start WordPress authorization
@app.get("/wordpress/connect")
async def wordpress_connect():

    if not settings.WORDPRESS_CLIENT_ID:
        return {
            "error": "WordPress Client ID is not configured"
        }

    if not settings.WORDPRESS_SITE_URL:
        return {
            "error": "WordPress site URL is not configured"
        }

    state = secrets.token_urlsafe(32)
    oauth_states.add(state)

    params = {
        "client_id": settings.WORDPRESS_CLIENT_ID,
        "redirect_uri": WORDPRESS_REDIRECT_URI,
        "response_type": "code",
        "scope": "posts",
        "state": state,
        "blog": settings.WORDPRESS_SITE_URL
    }

    authorization_url = (
        "https://public-api.wordpress.com/oauth2/authorize?"
        + urlencode(params)
    )

    return RedirectResponse(authorization_url)


# Step 2: Handle WordPress authorization callback
@app.get("/wordpress/callback")
async def wordpress_callback(
    code: str = None,
    state: str = None
):

    if not code or not state:
        return {
            "error": "Authorization code or state is missing"
        }

    if state not in oauth_states:
        return {
            "error": "Invalid OAuth state"
        }

    oauth_states.remove(state)

    token_url = (
        "https://public-api.wordpress.com/oauth2/token"
    )

    token_data = {
        "client_id": settings.WORDPRESS_CLIENT_ID,
        "client_secret": settings.WORDPRESS_CLIENT_SECRET,
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": WORDPRESS_REDIRECT_URI
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                token_url,
                data=token_data
            )

        response.raise_for_status()

        token_response = response.json()
        access_token = token_response.get("access_token")

        if not access_token:
            return {
                "error": "WordPress did not return an access token"
            }

        # Save the access token in the project's .env file
        env_path = (
            Path(__file__).resolve().parent.parent / ".env"
        )

        set_key(
            str(env_path),
            "WORDPRESS_ACCESS_TOKEN",
            access_token
        )

        return {
            "message": (
                "WordPress authorization successful. "
                "Access token saved securely."
            )
        }

    except httpx.HTTPError:
        return {
            "error": "Unable to complete WordPress token exchange"
        }


