from leapcell.table import LeapcellTable, LeapcellField, LeapcellFilter
import os
from typing import List, Tuple, Dict, Union


class Leapcell(object):
    """Leapcell is the main class of Leapcell SDK, it is used to create table client and config client."""

    default_base_url = "https://api.leapcell.io"

    def __init__(
        self, api_key: str, base_url: str | None = None, version: str = "v1"
    ) -> None:
        """_summary_

        Args:
            api_key (str): Bearer token for authentication, api_key is the api token of your Leapcell account, you can find it in your account page: leapcell.io/account.
            base_url (str, optional): base_url is the url of your Leapcell server, if you use the Leapcell cloud service, you can ignore this parameter. Defaults to None.
            version (str, optional): version is the version of Leapcell server, if you use the Leapcell cloud service, you can ignore this parameter. Defaults to "v1".

        Raises:
            Exception: api_key can not be empty, you can find it in your account page: leapcell.io/account
        """
        self._base_url = (
            base_url or os.environ.get("LEAPCELL_API_URL") or self.default_base_url
        )
        self._api_key = api_key or os.environ.get("LEAPCELL_API_TOKEN")
        if not api_key:
            raise Exception(
                "api_key can not be empty, you can find it in your account page: leapcell.io/account"
            )
        self._version = version

    def table(
        self, repository: str, table_id: str, name_type: str = "name"
    ) -> LeapcellTable:
        """table is used to create table instance.

        Args:
            repository (str): leapcell repository, you can find it in leapcell with format leapcell.io/{username}/{repo_name}, resource all have the same format as {username}/{repo_name}
            table_id (str): table id, you can find it in leapcell with format leapcell.io/{username}/{repo_name}/table/{table_id}, table_id all have the same format as {username}/{repo_name}/table/{table_id}
            name_type (str, optional): name_type is the type of the field, it can be "id" or "name". Defaults to "name". if it's "id", the field name will be "13145252145", "13145252147" ...; if it's "name", the field name will be "field-0", "field-1", "field-2", ...,

        Raises:
            ValueError: resource can not be empty
            ValueError: table_id can not be empty
            ValueError: api_key can not be empty

        Returns:
            LeapcellTable: LeapcellTable instance
        """
        if not repository:
            raise ValueError("repository can not be empty")
        if not table_id:
            raise ValueError("table_id can not be empty")
        if not self._api_key:
            raise ValueError("api_key can not be empty")

        return LeapcellTable(
            repository=repository,
            api_key=self._api_key,
            table_id=table_id,
            base_url=self._base_url,
            name_type=name_type,
            version=self._version,
        )
