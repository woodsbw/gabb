# Ignoring several pylint methods for now:
#   too-many-instance-attributes: We go over pylint's recommendation by one, but
#       leaving it as it makes sense....any other data construction I can come up
#       with would seem contrived.
#   too-many-arguments: We go over pylint's recommendation by one, but
#       leaving it as it makes sense....any other data construction I can come up
#       with would seem contrived or not expose things that could be useful to
#       configure in the future.
# pylint: disable=too-many-instance-attributes, too-many-arguments
"""Custom requests authentication for Gabb.

This contains the GabbAuth class, which is a custom authentication callable for
the requests library to handle authentication to the Smartcom FiLIP API that is
used by Gabb.

Example:
    session = requests.Session()
    session.auth = GabbAuth(username="username", password="password")
"""
import datetime
import json
import requests
from dateutil import parser


class GabbAuth(requests.auth.AuthBase):  # pylint: disable=too-few-public-methods
    """Custom requests authentication class for the Gabb API

    The Gabb API uses their own authentication scheme to generate auth and
    refresh tokens. This class implements that scheme as a custom
    authentication callable for the requests library.

    Attributes:
        username (str): Parent/guardian account username.
        password (str): Parent/guardian account password.
        auth_url (str): The API endpoint used to generate a fresh access token
            from the parent/guardian account username and password.
        refresh_url (str): The API endpoint used to generate an access token
            with the refresh token from the prior auth request.
        app_build (str): This is a standard string value that shouldn't be
            changed without knowing WHY you are doing it. Seems to be required
            for the API requests to be accepted and is probably used in
            some sort of server side reporting. The default value is currently
            working and shouldn't be set to something else without good reason.


    """

    _access_token = ""
    """str: The current active access token for the API. Do not manipulate directly."""
    _refresh_token = ""
    """str: The API endpoint used for token refresh. Do not manipulate directly."""
    _exp_date = ""
    """datetime.datetime: Datetime object representing when the current active
    token held in _access_token will expire."""
    _required_headers = {
        "X-Accept-Language": "en-US",
        "X-Accept-Offset": "-5.000000",
        "Accept-Version": "1.0",
        "User-Agent": "FiLIP-iOS",
        "X-Accept-Version": "1.0",
        "Content-Type": "application/json",
    }
    """dict: A dict of static headers that the API  requires in order to function properly"""

    def __init__(
        self,
        username: str,
        password: str,
        auth_url: str = "https://api.myfilip.com/v2/sso/gabb",
        refresh_url: str = "https://api.myfilip.com/v2/token/refresh",
        app_build: str = "1.28 (966)",
    ) -> None:
        """Initialize, set instance attributes and perform first authentication

        Args:
            username (str): Parent/guardian account username.
            password (str): Parent/guardian account password.
            auth_url (str, optional): The API endpoint used to generate a fresh
                access token from the parent/guardian account username and
                password.
            refresh_url (str, optional): The API endpoint used to generate an
                access token with the refresh token from the prior auth request.
            app_build (str, optional): Build version of the Gabb app we are
                emulating. Best left alone unless you have a specific use case.

        """
        self.username = username
        """str: Parent/guardian account username."""
        self.password = password
        """str: Parent/guardian account password."""
        self.auth_url = auth_url
        """ str: The API endpoint used to generate a fresh access token from the 
        parent/guardian account username and password."""
        self.refresh_url = refresh_url
        """str: The API endpoint used to generate an access token with the refresh 
        token from the prior auth request."""
        self.app_build = app_build
        """str: Build version of the Gabb app we are emulating. Best left alone unless 
        you have a specific use case."""

        self._new_authentication()

    def __call__(self, request: requests.Request) -> requests.Request:
        """Manipulate the request object to add the correct bearer token

        When the class is called, we check and see if the existing access token
        has expired, if it has, we refresh the token. We then (regardless if a
        refresh was needed or not) build the Authentication header and merge
        into existing request headers

        Args:
            request (request.Requests): The Request instance to be manipulated

        Returns:
            The manipulated Request instance with the Authentication header
            populated with the access bearer token.
        """
        if self._token_expired:
            self._refresh_authentication()

        request.headers.update({"Authorization": f"Bearer {self._access_token}"})

        return request

    def _new_authentication(self) -> None:
        """Performs a fresh authentication with username/password"""
        payload = json.dumps(
            {
                "appBuild": self.app_build,
                "username": self.username,
                "password": self.password,
            }
        )

        resp = requests.post(
            self.auth_url, headers=self._required_headers, data=payload, timeout=15
        )

        self._update_tokens_from_response(response=resp)

    def _refresh_authentication(self) -> None:
        """Performs an API token refresh"""
        payload = json.dumps({"refreshToken": self._refresh_token})

        resp = requests.post(
            self.refresh_url, headers=self._required_headers, data=payload, timeout=15
        )

        self._update_tokens_from_response(response=resp)

    def _update_tokens_from_response(self, response: requests.Response) -> None:
        """Takes a requests.Response object and sets token and expiration attributes"""
        resp_data = response.json()

        self._access_token = resp_data["data"]["accessToken"]
        self._refresh_token = resp_data["data"]["refreshToken"]
        self._exp_date = parser.parse(resp_data["data"]["expDate"])

    @property
    def _token_expired(self) -> bool:
        """bool: Returns True if the current active access token has expired and False
        if it hasn't"""
        return self._exp_date < datetime.datetime.now(datetime.timezone.utc)
