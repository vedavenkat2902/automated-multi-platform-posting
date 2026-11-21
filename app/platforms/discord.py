
import httpx
from datetime import datetime, timezone

from app.config import settings
from app.platforms.base import BasePlatform


class DiscordPlatform(BasePlatform):

    def __init__(self):
        super().__init__("Discord")

    async def publish(self, message: str) -> dict:

        webhook_url = settings.DISCORD_WEBHOOK_URL

        if not webhook_url:
            return self.failure_result(
                "Discord webhook URL is not configured"
            )

        # Validate the configured webhook URL
        if not webhook_url.startswith(
            "https://discord.com/api/webhooks/"
        ):
            return self.failure_result(
                "Invalid Discord webhook URL"
            )

        try:
            async with httpx.AsyncClient(timeout=20.0) as client:

                # wait=true returns the created message
                response = await client.post(
                    webhook_url,
                    params={"wait": "true"},
                    json={
                        "content": message,
                        "allowed_mentions": {
                            "parse": []
                        }
                    }
                )

                response.raise_for_status()

                result = response.json()

                if not isinstance(result, dict):
                    return self.failure_result(
                        "Invalid response received from Discord"
                    )

                message_id = result.get("id")
                channel_id = result.get("channel_id")
                created_at = result.get("timestamp")

                if (
                    not message_id
                    or not channel_id
                    or not created_at
                ):
                    return self.failure_result(
                        "Discord returned incomplete message details"
                    )

                # Convert Discord timestamp to UTC
                timestamp = datetime.fromisoformat(
                    created_at.replace("Z", "+00:00")
                ).astimezone(timezone.utc)

                # A public message URL cannot be confirmed
                # without the necessary server/channel visibility details.
                posted_url = None
                public_access = None

                return self.success_result(
                    posted_url=posted_url,
                    public_access=public_access,
                    date=timestamp.strftime("%Y-%m-%d"),
                    time=timestamp.strftime("%H:%M:%S")
                )

        except httpx.HTTPStatusError as error:
            return self.failure_result(
                f"Discord API error: HTTP {error.response.status_code}"
            )

        except httpx.RequestError:
            return self.failure_result(
                "Unable to connect to Discord API"
            )

        except (KeyError, ValueError, TypeError, AttributeError):
            return self.failure_result(
                "Invalid response received from Discord"
            )
