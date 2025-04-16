import os
import requests
from typing import Dict, Optional


class GistManager:
    def __init__(self,
                 token: Optional[str] = None
                 ):
        """Initialize the GistManager with a GitHub token.

        Args:
            token: GitHub personal access token. If not provided, will try to get from environment.
        """
        self.token = token or os.getenv('GITHUB_GIST_TOKEN')
        if not self.token:
            raise ValueError("GitHub token not provided and GITHUB_GIST_TOKEN environment variable not set")

        self.headers = {
            'Authorization': f'token {self.token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        self.api_url = 'https://api.github.com/gists'

    def create_gist(self,
                    content: str,
                    filename: str,
                    description: str,
                    public: bool = False
                    ) -> Dict:
        """Create a new Gist with the given content.

        Args:
            content: The content to put in the gist
            filename: Name of the file in the gist
            description: Description of the gist
            public: Whether the gist should be public

        Returns:
            Dict containing the gist data including the URL
        """
        payload = {
            "description": description,
            "public": public,
            "files": {
                filename: {
                    "content": content
                }
            }
        }

        response = requests.post(
            self.api_url,
            headers=self.headers,
            json=payload
        )

        if response.status_code != 201:
            raise Exception(f"Failed to create gist: {response.text}")

        return response.json()

    def get_gist(self,
                 gist_id: str
                 ) -> Dict:
        """Retrieve a specific gist by ID.

        Args:
            gist_id: The ID of the gist to retrieve

        Returns:
            Dict containing the gist data
        """
        response = requests.get(
            f"{self.api_url}/{gist_id}",
            headers=self.headers
        )

        if response.status_code != 200:
            raise Exception(f"Failed to retrieve gist: {response.text}")

        return response.json()