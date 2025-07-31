import uuid
from .Base import BaseAPI


class Asset(BaseAPI):
    def __init__(self, connector):
        super().__init__(connector)
        self.__base_api = connector.api + "/assets"

    def _get(self, url: str = None, params: dict = None, headers: dict = None):
        """
        Makes a GET request to the asset API.
        :param url: The URL to send the GET request to.
        :param params: Optional parameters to include in the GET request.
        :param headers: Optional headers to include in the GET request.
        :return: The response from the GET request.
        """
        return super()._get(self.__base_api if not url else url, params, headers)

    def _post(self, url: str, data: dict):
        """
        Makes a POST request to the asset API.
        :param url: The URL to send the POST request to.
        :param data: The data to send in the POST request.
        :return: The response from the POST request.
        """
        return super()._post(url, data)

    def _handle_response(self, response):
        return super()._handle_response(response)

    def _uuid_validation(self, id):
        return super()._uuid_validation(id)

    def get_asset(self, asset_id):
        """
        Retrieves an asset by its ID.
        :param asset_id: The ID of the asset to retrieve.
        :return: Asset details.
        """
        response = self._get(url=f"{self.__base_api}/{asset_id}")
        return self._handle_response(response)

    def add_asset(
        self,
        name: str,
        domain_id: str,
        display_name: str = None,
        type_id: str = None,
        id: str = None,
        status_id: str = None,
        excluded_from_auto_hyperlink: bool = False,
        type_public_id: str = None,
    ):
        """
        Adds a new asset.
        :param name: The name of the asset.
        :param domain_id: The ID of the domain to which the asset belongs.
        :param display_name: Optional display name for the asset.
        :param type_id: Optional type ID for the asset.
        :param id: Optional ID for the asset.
        :param status_id: Optional status ID for the asset.
        :param excluded_from_auto_hyperlink: Whether the asset is excluded from auto hyperlinking.
        :param type_public_id: Optional public ID for the asset type.
        :return: Details of the created asset.
        """
        # Parameter type validation
        if not name or not domain_id:
            raise ValueError("Name and domain_id are required parameters.")
        if not isinstance(excluded_from_auto_hyperlink, bool):
            raise ValueError("excluded_from_auto_hyperlink must be a boolean value.")
        if type_id and not isinstance(type_id, str):
            raise ValueError("type_id must be a string if provided.")
        if id and not isinstance(id, str):
            raise ValueError("id must be a string if provided.")
        if status_id and not isinstance(status_id, str):
            raise ValueError("status_id must be a string if provided.")
        if type_public_id and not isinstance(type_public_id, str):
            raise ValueError("type_public_id must be a string if provided.")

        # Check Ids are UUIDS
        if id and self._uuid_validation(id) is False:
            raise ValueError("id must be a valid UUID.")
        if domain_id and self._uuid_validation(domain_id) is False:
            raise ValueError("domain_id must be a valid UUID.")
        if type_id and self._uuid_validation(type_id) is False:
            raise ValueError("type_id must be a valid UUID.")
        if status_id and self._uuid_validation(status_id) is False:
            raise ValueError("status_id must be a valid UUID.")

        data = {
            "name": name,
            "domainId": domain_id,
            "displayName": display_name,
            "typeId": type_id,
            "id": id,
            "statusId": status_id,
            "excludedFromAutoHyperlink": excluded_from_auto_hyperlink,
            "typePublicId": type_public_id
        }
        response = self._post(url=self.__base_api, data=data)
        return self._handle_response(response)
