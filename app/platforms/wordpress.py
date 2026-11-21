
from datetime import datetime, timezone
from urllib.parse import urlparse

import httpx

from app.config import settings
from app.platforms.base import BasePlatform


class WordPressPlatform(BasePlatform):

    def __init__(self):
        super().__init__("WordPress")

    async def publish(self, message: str) -> dict:

        # Check WordPress credentials
        if not settings.WORDPRESS_ACCESS_TOKEN:
            return self.failure_result(
                "WordPress access token is not configured"
            )

        if not settings.WORDPRESS_SITE_URL:
            return self.failure_result(
                "WordPress site URL is not configured"
            )

        # Extract the site domain
        parsed_url = urlparse(settings.WORDPRESS_SITE_URL)
        site_domain = parsed_url.netloc

        if not site_domain:
            return self.failure_result(
                "Invalid WordPress site URL"
            )

        # WordPress API endpoint
        api_url = (
            f"https://public-api.wordpress.com/rest/v1.1/"
            f"sites/{site_domain}/posts/new"
        )

        # Prepare the post
        post_data = {
            "title": "Update from Automated Posting System",
            "content": message,
            "status": "publish"
        }

        headers = {
            "Authorization": (
                f"Bearer {settings.WORDPRESS_ACCESS_TOKEN}"
            )
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:

                response = await client.post(
                    api_url,
                    headers=headers,
                    data=post_data
                )

            response.raise_for_status()

            result = response.json()

            # Validate the API response
            if not isinstance(result, dict):
                return self.failure_result(
                    "Invalid response from WordPress"
                )

            posted_url = result.get("URL")
            post_status = result.get("status")
            created_at = result.get("date")

            if not posted_url or post_status != "publish":
                return self.failure_result(
                    "WordPress did not confirm post publication"
                )

            # Convert WordPress timestamp to UTC
            if created_at:
                post_datetime = datetime.fromisoformat(
                    created_at.replace("Z", "+00:00")
                )
                post_datetime = post_datetime.astimezone(
                    timezone.utc
                )
            else:
                post_datetime = datetime.now(timezone.utc)

            return self.success_result(
                posted_url=posted_url,
                public_access=True,
                date=post_datetime.strftime("%Y-%m-%d"),
                time=post_datetime.strftime("%H:%M:%S")
            )

        except httpx.HTTPStatusError as error:
            return self.failure_result(
                f"WordPress API error: HTTP {error.response.status_code}"
            )

        except httpx.RequestError:
            return self.failure_result(
                "Unable to connect to WordPress API"
            )

        except (ValueError, TypeError, AttributeError):
            return self.failure_result(
                "Unable to process WordPress API response"
            )
