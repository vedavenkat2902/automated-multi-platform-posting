
import httpx
from datetime import datetime, timezone

from app.config import settings
from app.platforms.base import BasePlatform


class TelegramPlatform(BasePlatform):

    def __init__(self):
        super().__init__("Telegram")

    async def publish(self, message: str) -> dict:

        bot_token = settings.TELEGRAM_BOT_TOKEN
        chat_id = settings.TELEGRAM_CHAT_ID

        if not bot_token or not chat_id:
            return self.failure_result(
                "Telegram credentials are not configured"
            )

        api_url = (
            f"https://api.telegram.org/bot{bot_token}/sendMessage"
        )

        payload = {
            "chat_id": chat_id,
            "text": message,
            "link_preview_options": {
                "is_disabled": False
            }
        }

        try:
            async with httpx.AsyncClient(timeout=20.0) as client:

                response = await client.post(
                    api_url,
                    json=payload
                )

                response.raise_for_status()

                result = response.json()

                if not isinstance(result, dict):
                    return self.failure_result(
                        "Invalid response received from Telegram"
                    )

                if not result.get("ok"):
                    return self.failure_result(
                        result.get(
                            "description",
                            "Telegram API failed"
                        )
                    )

                sent_message = result.get("result", {})

                if not isinstance(sent_message, dict):
                    return self.failure_result(
                        "Telegram returned invalid message details"
                    )

                message_id = sent_message.get("message_id")
                sent_date = sent_message.get("date")
                chat = sent_message.get("chat", {})

                if (
                    message_id is None
                    or sent_date is None
                    or not isinstance(chat, dict)
                ):
                    return self.failure_result(
                        "Telegram returned incomplete message details"
                    )

                # Convert Telegram's Unix timestamp to UTC
                timestamp = datetime.fromtimestamp(
                    sent_date,
                    tz=timezone.utc
                )

                # Construct a public URL when possible
                username = chat.get("username")
                chat_type = chat.get("type")

                posted_url = None
                public_access = False

                if username and chat_type in ("channel", "supergroup"):
                    posted_url = (
                        f"https://t.me/{username}/{message_id}"
                    )
                    public_access = True

                return self.success_result(
                    posted_url=posted_url,
                    public_access=public_access,
                    date=timestamp.strftime("%Y-%m-%d"),
                    time=timestamp.strftime("%H:%M:%S")
                )

        except httpx.HTTPStatusError as error:
            return self.failure_result(
                f"Telegram API error: HTTP {error.response.status_code}"
            )

        except httpx.RequestError:
            return self.failure_result(
                "Unable to connect to Telegram API"
            )

        except (KeyError, ValueError, TypeError, AttributeError):
            return self.failure_result(
                "Invalid response received from Telegram"
            )
