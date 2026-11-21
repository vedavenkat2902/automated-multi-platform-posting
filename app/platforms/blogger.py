
from datetime import datetime, timezone
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from app.config import settings
from app.platforms.base import BasePlatform


class BloggerPlatform(BasePlatform):

    def __init__(self):
        super().__init__("Blogger")

    async def publish(self, message: str) -> dict:

        token_file = Path(__file__).resolve().parents[2] / "token.json"

        if not settings.BLOGGER_BLOG_ID:
            return self.failure_result(
                "Blogger Blog ID is not configured"
            )

        if not token_file.exists():
            return self.failure_result(
                "Blogger authentication token is missing"
            )

        try:
            credentials = Credentials.from_authorized_user_file(
                str(token_file),
                ["https://www.googleapis.com/auth/blogger"]
            )

            if not credentials.valid:
                if credentials.expired and credentials.refresh_token:
                    credentials.refresh(Request())

                    token_file.write_text(
                        credentials.to_json(),
                        encoding="utf-8"
                    )
                else:
                    return self.failure_result(
                        "Blogger authentication has expired. "
                        "Please authenticate again."
                    )

            service = build(
                "blogger",
                "v3",
                credentials=credentials,
                cache_discovery=False
            )

            # Create a published Blogger post
            post = {
                "kind": "blogger#post",
                "title": "Update from Automated Posting System",
                "content": message
            }

            result = service.posts().insert(
                blogId=settings.BLOGGER_BLOG_ID,
                body=post,
                isDraft=False
            ).execute()

            posted_url = result.get("url")
            post_status = result.get("status")

            if not posted_url or post_status != "LIVE":
                return self.failure_result(
                    "Blogger did not confirm post publication"
                )

            published_at = result.get("published")

            if published_at:
                post_datetime = datetime.fromisoformat(
                    published_at.replace("Z", "+00:00")
                ).astimezone(timezone.utc)
            else:
                post_datetime = datetime.now(timezone.utc)

            return self.success_result(
                posted_url=posted_url,
                public_access=True,
                date=post_datetime.strftime("%Y-%m-%d"),
                time=post_datetime.strftime("%H:%M:%S")
            )

        except HttpError as error:
            return self.failure_result(
                f"Blogger API error: HTTP {error.resp.status}"
            )

        except Exception:
            return self.failure_result(
                "Unable to publish the post to Blogger"
            )
