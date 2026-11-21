
from datetime import datetime, timezone

import httpx

from app.config import settings
from app.platforms.base import BasePlatform


class DevToPlatform(BasePlatform):

    def __init__(self):
        super().__init__("DEV Community")

    async def publish(self, message: str) -> dict:

        if not settings.DEVTO_API_KEY:
            return self.failure_result(
                "DEV Community API key is not configured"
            )

        api_url = "https://dev.to/api/articles"

        headers = {
            "api-key": settings.DEVTO_API_KEY,
            "Content-Type": "application/json"
        }

        article_data = {
            "article": {
                "title": "Update from Automated Multi-Platform Posting System",
                "body_markdown": message,
                "published": True
            }
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    api_url,
                    headers=headers,
                    json=article_data
                )

            response.raise_for_status()

            result = response.json()

            if not isinstance(result, dict):
                return self.failure_result(
                    "Invalid response from DEV Community"
                )

            article_url = result.get("url")

            if not article_url:
                return self.failure_result(
                    "DEV Community did not return an article URL"
                )

            post_datetime = datetime.now(timezone.utc)

            return self.success_result(
                posted_url=article_url,
                public_access=True,
                date=post_datetime.strftime("%Y-%m-%d"),
                time=post_datetime.strftime("%H:%M:%S")
            )

        except httpx.HTTPStatusError as error:
            return self.failure_result(
                f"DEV Community API error: HTTP {error.response.status_code}"
            )

        except httpx.RequestError:
            return self.failure_result(
                "Unable to connect to DEV Community API"
            )

        except (ValueError, TypeError, AttributeError):
            return self.failure_result(
                "Unable to process DEV Community response"
            )
