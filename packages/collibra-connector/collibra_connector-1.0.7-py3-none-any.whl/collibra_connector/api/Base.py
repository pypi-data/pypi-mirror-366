import requests
from .Exceptions import (
    UnauthorizedError,
    ForbiddenError,
    NotFoundError,
    ServerError
)

class BaseAPI:
    def __init__(self, connector):
        self.__connector = connector
        self.__base_api = connector.api
        self.__header = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        self.__params = None

    def __get(self, url: str = None, params: dict = None, headers: dict = None):
        """
        Makes a GET request to the specified URL.
        :param url: The URL to send the GET request to.
        :param params: Optional parameters to include in the GET request.
        :param headers: Optional headers to include in the GET request.
        :return: The response from the GET request.
        """
        url = self.__base_api if not url else url
        headers = self.__header if not headers else headers
        params = self.__params if not params else params
        return requests.get(
            url,
            auth=self.__connector.auth,
            params=params,
            headers=headers
        )

    def __post(self, url: str, data: dict, headers: dict = None):
        """
        Makes a POST request to the specified URL with the given data.
        :param url: The URL to send the POST request to.
        :param data: The data to send in the POST request.
        :return: The response from the POST request.
        """
        url = self.__base_api if not url else url
        headers = self.__header if not headers else headers
        if not isinstance(data, dict):
            raise ValueError("Data must be a dictionary")
        if not data:
            raise ValueError("Data cannot be empty")
        return requests.post(
            url,
            auth=self.__connector.auth,
            json=data,
            headers=self.__header
        )

    def __handle_response(self, response):
        """
        Handles the response from the API.
        :param response: The response object from the API request.
        :return: The JSON content of the response if successful, otherwise raises an error.
        """
        if response.status_code == 200 or response.status_code == 201:
            return response.json()
        elif response.status_code == 401:
            raise UnauthorizedError("Unauthorized access - invalid credentials")
        elif response.status_code == 403:
            raise ForbiddenError("Forbidden access - insufficient permissions")
        elif response.status_code == 404:
            raise NotFoundError("The specified resource was not found")
        elif response.status_code >= 500:
            raise ServerError("Internal server error - something went wrong on the server")
