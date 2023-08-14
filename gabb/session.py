"""Custom requests session for Gabb.

This contains the GabbSession class, which is extended from requests.Session and 
includes the use of GabbAuth as the authentication handler and base URL management.

Example:
    session = GabbSession(
        username="username",
        password="password",
        base_url="https://api.myfilip.com/v2/",
        alt_base_url="https://api.myfilip.com/",
    )

    resp = session.get("constants")
"""

from urllib.parse import urljoin
import requests
from gabb.auth import GabbAuth


class GabbSession(requests.Session):
    """Custom Session class to add base URL functionality and handle the custom
    auth object"""

    def __init__(
        self,
        username: str,
        password: str,
        base_url: str = None,
        alt_base_url: str = None,
    ) -> None:
        """Catch and set base_url on instance, then pass up to requests.Session"""
        super().__init__()
        self.base_url = base_url
        """Base URL for the session"""
        self.alt_base_url = alt_base_url
        """Alternative base URL for the session"""
        self.use_alt_base_url_next_request = False
        """Flag to use alternative base URL for the session"""
        self.auth = GabbAuth(username=username, password=password)

    def request(self, method: str, url: str, *args, **kwargs) -> requests.Request:
        """Catch and inject in the base_url (or alt_base_url), then pass up to
        requests.request()"""

        # If the use_alt_base_url_next_request flag is true, use alt base URL,
        # then set flag to False. Otherwise, use base URL
        if self.use_alt_base_url_next_request:
            joined_url = urljoin(self.alt_base_url, url)
            self.use_alt_base_url_next_request = False
        else:
            joined_url = urljoin(self.base_url, url)

        return super().request(method, joined_url, *args, **kwargs)
