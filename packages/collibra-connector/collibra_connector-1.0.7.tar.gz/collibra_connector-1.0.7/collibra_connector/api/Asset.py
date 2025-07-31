from .Base import BaseAPI

class Asset(BaseAPI):
    def __init__(self, connector):
        super().__init__(connector)
        self.__base_api = connector.api + "/assets"

    def __get(self, url: str = None, params: dict = None, headers: dict = None):
        """
        Makes a GET request to the asset API.
        :param url: The URL to send the GET request to.
        :param params: Optional parameters to include in the GET request.
        :param headers: Optional headers to include in the GET request.
        :return: The response from the GET request.
        """
        return super().__get(self.__base_api if not url else url, params, headers)

    def __post(self, url: str, data: dict):
        """
        Makes a POST request to the asset API.
        :param url: The URL to send the POST request to.
        :param data: The data to send in the POST request.
        :return: The response from the POST request.
        """
        return super().__post(url, data)

    def __handle_response(self, response):
        return super().__handle_response(response)
    
    def get_asset(self, asset_id):
        """
        Retrieves an asset by its ID.
        :param asset_id: The ID of the asset to retrieve.
        :return: Asset details.
        """
        response = self.__get(url=f"{self.__base_api}/{asset_id}")
        return self.__handle_response(response)

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
        response = self.__post(url=self.__base_api, data=data)
        return self.__handle_response(response)
