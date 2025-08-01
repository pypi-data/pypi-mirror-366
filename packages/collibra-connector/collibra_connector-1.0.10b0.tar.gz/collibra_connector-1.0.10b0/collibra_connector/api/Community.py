import uuid
from .Base import BaseAPI


class Community(BaseAPI):
    def __init__(self, connector):
        super().__init__(connector)
        self.__base_api = connector.api + "/communities"

    def get_community(self, community_id: str):
        """
        Get a community by its ID.
        :param community_id: The ID of the community to retrieve.
        :return: Community details.
        """
        if not community_id:
            raise ValueError("community_id is required")
        if not isinstance(community_id, str):
            raise ValueError("community_id must be a string")

        try:
            uuid.UUID(community_id)
        except ValueError as exc:
            raise ValueError("community_id must be a valid UUID") from exc

        response = self._get(url=f"{self.__base_api}/{community_id}")
        return self._handle_response(response)

    def find_communities(
        self,
        sort_field: str = "NAME",
        count_limit: int = -1,
        cursor: str = None,
        exclude_meta: bool = True,
        limit: int = 0,
        name: str = None,
        name_match_mode: str = "ANYWHERE",
        offset: int = 0,
        parent_id: str = None,
        sort_order: str = "ASC"
    ):
        """
        Find communities matching the given search criteria.
        :param sort_field: Field to sort results by. Options: NAME, CREATED_BY, CREATED_ON, LAST_MODIFIED, ID
        :param count_limit: Limit elements counted. -1 counts all, 0 skips count. Ignored with cursor pagination.
        :param cursor: Cursor for pagination. Pass empty string for first page, use nextCursor for subsequent pages.
        :param exclude_meta: Whether to exclude meta communities (not manually created by users).
        :param limit: Maximum results to retrieve. 0 uses default, max 1000.
        :param name: Name of community to search for.
        :param name_match_mode: Name matching mode. Options: START, END, ANYWHERE, EXACT
        :param offset: First result to retrieve (deprecated, use cursor instead).
        :param parent_id: Parent community ID to filter by.
        :param sort_order: Sort order. Options: ASC, DESC
        :return: List of communities matching criteria.
        """
        # Validate sort_field
        valid_sort_fields = ["NAME", "CREATED_BY", "CREATED_ON", "LAST_MODIFIED", "ID"]
        if sort_field not in valid_sort_fields:
            raise ValueError(f"sort_field must be one of: {', '.join(valid_sort_fields)}")

        # Validate name_match_mode
        valid_match_modes = ["START", "END", "ANYWHERE", "EXACT"]
        if name_match_mode not in valid_match_modes:
            raise ValueError(f"name_match_mode must be one of: {', '.join(valid_match_modes)}")

        # Validate sort_order
        if sort_order not in ["ASC", "DESC"]:
            raise ValueError("sort_order must be 'ASC' or 'DESC'")

        # Validate limit
        if limit < 0 or limit > 1000:
            raise ValueError("limit must be between 0 and 1000")

        # Validate parent_id if provided
        if parent_id is not None:
            if not isinstance(parent_id, str):
                raise ValueError("parent_id must be a string")
            try:
                uuid.UUID(parent_id)
            except ValueError as exc:
                raise ValueError("parent_id must be a valid UUID") from exc

        # Validate cursor and offset usage
        if cursor is not None and offset != 0:
            raise ValueError("Cannot use both cursor and offset in the same request")

        # Build parameters - only include non-default values
        params = {}

        if sort_field != "NAME":
            params["sortField"] = sort_field
        if count_limit != -1:
            params["countLimit"] = count_limit
        if cursor is not None:
            params["cursor"] = cursor
        if exclude_meta is not True:
            params["excludeMeta"] = exclude_meta
        if limit != 0:
            params["limit"] = limit
        if name is not None:
            params["name"] = name
        if name_match_mode != "ANYWHERE":
            params["nameMatchMode"] = name_match_mode
        if offset != 0:
            params["offset"] = offset
        if parent_id is not None:
            params["parentId"] = parent_id
        if sort_order != "ASC":
            params["sortOrder"] = sort_order

        response = self._get(params=params)
        return self._handle_response(response)
