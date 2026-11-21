
import asyncio
from typing import List

from app.platforms.base import BasePlatform


class PostingService:
    """
    Coordinates message publishing across multiple platforms.
    """

    def __init__(self, platforms: List[BasePlatform]):
        self.platforms = platforms

    async def post_to_platform(
        self,
        platform: BasePlatform,
        message: str
    ) -> dict:
        """
        Publish to one platform independently.
        """

        try:
            result = await platform.publish(message)

            if not isinstance(result, dict):
                return platform.failure_result(
                    "Invalid response returned by platform"
                )

            if result.get("status") not in ("success", "failed"):
                return platform.failure_result(
                    "Platform returned an invalid status"
                )

            return result

        except Exception as error:
            return platform.failure_result(str(error))

    async def post_message(self, message: str) -> dict:
        """
        Publish the message to all platforms concurrently.
        """

        tasks = [
            self.post_to_platform(platform, message)
            for platform in self.platforms
        ]

        results = await asyncio.gather(*tasks)

        success = any(
            result["status"] == "success"
            for result in results
        )

        return {
            "success": success,
            "results": results
        }
