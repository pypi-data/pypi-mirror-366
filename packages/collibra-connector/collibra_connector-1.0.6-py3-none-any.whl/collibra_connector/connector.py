import logging
import requests
from requests.auth import HTTPBasicAuth

from .api import Asset

class CollibraConnector():
    """
    This class is used to connect to the Collibra API.
    It requires the API URL and authentication credentials.
    The authentication is done using HTTP Basic Auth.
    """

    def __init__(self, api: str, username: str, password: str, timeout: int = 30):
        """
        Initializes the CollibraConnector with API URL and authentication credentials.
        :param api: The API URL for Collibra.
        :param username: The username for authentication.
        :param password: The password for authentication.
        """
        self.__auth = HTTPBasicAuth(username, password)
        self.__api = api + "/rest/2.0"
        self.__base_url = api
        self.__timeout = timeout

        self.asset = Asset(self)

        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def __repr__(self):
        return f"CollibraConnector(api={self.__api}, auth={self.__auth})"

    def test_connection(self):
        """Test the connection to Collibra API"""
        try:
            response = requests.get(
                f"{self.__api}/info",
                auth=self.__auth,
                timeout=self.__timeout
            )
            return response.status_code == 200
        except Exception as e:
            self.logger.error(f"Connection test failed: {e}")
            return False

    @property
    def api(self):
        return self.__api

    @property
    def auth(self):
        return self.__auth

    @property
    def base_url(self):
        return self.__base_url