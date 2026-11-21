import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()


class Settings:

    # WordPress
    WORDPRESS_CLIENT_ID = os.getenv("WORDPRESS_CLIENT_ID")
    WORDPRESS_CLIENT_SECRET = os.getenv("WORDPRESS_CLIENT_SECRET")
    WORDPRESS_SITE_URL = os.getenv("WORDPRESS_SITE_URL")
    WORDPRESS_ACCESS_TOKEN = os.getenv("WORDPRESS_ACCESS_TOKEN")

    # Blogger
    BLOGGER_BLOG_ID = os.getenv("BLOGGER_BLOG_ID")

    # DEV Community
    DEVTO_API_KEY = os.getenv("DEVTO_API_KEY")

    # Telegram
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
    TELEGRAM_CHANNEL_USERNAME = os.getenv(
        "TELEGRAM_CHANNEL_USERNAME"
    )

    # Discord
    DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")


settings = Settings()