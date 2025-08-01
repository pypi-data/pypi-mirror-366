import os
import time
from typing import Optional, Tuple

import requests
from dotenv import load_dotenv


class Authorization:
    def __init__(self):
        """Initialize the Authorization class
        
        Load configuration from environment variables or .env file
        """
        # Load environment variables
        load_dotenv()

        # Get configuration from environment variables
        self.app_id = os.getenv('QJ_APP_ID')
        self.app_secret = os.getenv('QJ_APP_SECRET')
        self.host = os.getenv('QJ_APP_HOST', 'https://uat-open.qj-robots.com')

        if not self.app_id or not self.app_secret:
            raise ValueError('Environment variables APP_ID and APP_SECRET must be set')

        self._access_token: Optional[str] = None
        self._expire_time: Optional[float] = None

    def _fetch_access_token(self) -> Tuple[str, int]:
        """Fetch new access token from server
        
        Returns:
            tuple: (access_token, expire_in)
        """
        url = f"{self.host}/open-api/open-apis/base/auth/access_token"
        params = {
            "app_id": self.app_id,
            "app_secret": self.app_secret
        }

        response = requests.get(url, params=params)
        response.raise_for_status()

        data = response.json()
        if data["code"] != 0:
            raise Exception(f"Failed to get access token: {data['message']}")

        return data["data"]["accessToken"], data["data"]["expire"]

    def get_access_token(self) -> str:
        """Get a valid access token
        
        If the token doesn't exist or is about to expire, it will automatically fetch a new one
        
        Returns:
            str: A valid access token
        """
        # Check if token needs refresh (refresh 5 minutes before expiration)
        if (self._access_token is None or
                self._expire_time is None or
                time.time() + 300 >= self._expire_time):
            token, expire_in = self._fetch_access_token()
            self._access_token = token
            self._expire_time = time.time() + expire_in

        return self._access_token
