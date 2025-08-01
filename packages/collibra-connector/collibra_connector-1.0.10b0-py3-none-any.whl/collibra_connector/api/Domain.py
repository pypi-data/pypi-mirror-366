import uuid
from .Base import BaseAPI


class Domain(BaseAPI):
    def __init__(self, connector):
        super().__init__(connector)
        self.__base_api = connector.api + "/domains"

    def get_domain(self, domain_id: str):
        """
        Get a domain by its ID.
        :param domain_id: The ID of the domain to retrieve.
        :return: Domain details.
        """
        if not domain_id:
            raise ValueError("domain_id is required")
        if not isinstance(domain_id, str):
            raise ValueError("domain_id must be a string")

        try:
            uuid.UUID(domain_id)
        except ValueError as exc:
            raise ValueError("domain_id must be a valid UUID") from exc

        response = self._get(url=f"{self.__base_api}/{domain_id}")
        return self._handle_response(response)

    def find_domains(
        self,
        community_id: str = None,
        count_limit: int = -1,
        cursor: str = None,
        exclude_meta: bool = True,
        include_sub_communities: bool = False,
        limit: int = 0,
        name: str = None,
        name_match_mode: str = "ANYWHERE",
        offset: int = 0,
        type_id: str = None,
        type_public_id: str = None
    ):
        """
        Find domains matching the given search criteria.
        :param community_id: ID of the community to find domains in.
        :param count_limit: Limit elements counted. -1 counts all, 0 skips count. Ignored with cursor pagination.
        :param cursor: Cursor for pagination. Pass empty string for first page, use nextCursor for subsequent pages.
        :param exclude_meta: Whether to exclude meta domains (not manually created by users).
        :param include_sub_communities: Whether to search in sub-communities of the specified community.
        :param limit: Maximum results to retrieve. 0 uses default, max 1000.
        :param name: Name of domain to search for.
        :param name_match_mode: Name matching mode. Options: START, END, ANYWHERE, EXACT
        :param offset: First result to retrieve (deprecated, use cursor instead).
        :param type_id: Domain type ID to filter by.
        :param type_public_id: Domain type public ID to filter by.
        :return: List of domains matching criteria.
        """
        # Validate name_match_mode
        valid_match_modes = ["START", "END", "ANYWHERE", "EXACT"]
        if name_match_mode not in valid_match_modes:
            raise ValueError(f"name_match_mode must be one of: {', '.join(valid_match_modes)}")

        # Validate limit
        if limit < 0 or limit > 1000:
            raise ValueError("limit must be between 0 and 1000")

        # Validate community_id if provided
        if community_id is not None:
            if not isinstance(community_id, str):
                raise ValueError("community_id must be a string")
            try:
                uuid.UUID(community_id)
            except ValueError as exc:
                raise ValueError("community_id must be a valid UUID") from exc

        # Validate type_id if provided
        if type_id is not None:
            if not isinstance(type_id, str):
                raise ValueError("type_id must be a string")
            try:
                uuid.UUID(type_id)
            except ValueError as exc:
                raise ValueError("type_id must be a valid UUID") from exc

        # Validate cursor and offset usage
        if cursor is not None and offset != 0:
            raise ValueError("Cannot use both cursor and offset in the same request")

        # Build parameters - only include non-default values
        params = {}

        if community_id is not None:
            params["communityId"] = community_id
        if count_limit != -1:
            params["countLimit"] = count_limit
        if cursor is not None:
            params["cursor"] = cursor
        if exclude_meta is not True:
            params["excludeMeta"] = exclude_meta
        if include_sub_communities is not False:
            params["includeSubCommunities"] = include_sub_communities
        if limit != 0:
            params["limit"] = limit
        if name is not None:
            params["name"] = name
        if name_match_mode != "ANYWHERE":
            params["nameMatchMode"] = name_match_mode
        if offset != 0:
            params["offset"] = offset
        if type_id is not None:
            params["typeId"] = type_id
        if type_public_id is not None:
            params["typePublicId"] = type_public_id

        response = self._get(params=params)
        return self._handle_response(response)
