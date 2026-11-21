
from abc import ABC, abstractmethod
from typing import Optional


class BasePlatform(ABC):
    """
    Base class for all third-party platform integrations.
    """

    def __init__(self, platform_name: str):
        self.platform_name = platform_name

    @abstractmethod
    async def publish(self, message: str) -> dict:
        """
        Publish a message to the platform.
        """
        pass

    def success_result(
        self,
        posted_url: Optional[str],
        public_access: Optional[bool],
        date: str,
        time: str
    ) -> dict:
        return {
            "platform": self.platform_name,
            "status": "success",
            "posted_url": posted_url,
            "public_access": public_access,
            "date": date,
            "time": time,
            "error": None
        }

    def failure_result(self, error: str) -> dict:
        return {
            "platform": self.platform_name,
            "status": "failed",
            "posted_url": None,
            "public_access": None,
            "date": None,
            "time": None,
            "error": error
        }
