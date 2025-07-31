"""
Type annotations for workspaces-web service client paginators.

[Documentation](https://youtype.github.io/types_boto3_docs/types_boto3_workspaces_web/paginators/)

Copyright 2025 Vlad Emelianov

Usage::

    ```python
    from boto3.session import Session

    from types_boto3_workspaces_web.client import WorkSpacesWebClient
    from types_boto3_workspaces_web.paginator import (
        ListDataProtectionSettingsPaginator,
        ListSessionsPaginator,
    )

    session = Session()
    client: WorkSpacesWebClient = session.client("workspaces-web")

    list_data_protection_settings_paginator: ListDataProtectionSettingsPaginator = client.get_paginator("list_data_protection_settings")
    list_sessions_paginator: ListSessionsPaginator = client.get_paginator("list_sessions")
    ```
"""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

from botocore.paginate import PageIterator, Paginator

from .type_defs import (
    ListDataProtectionSettingsRequestPaginateTypeDef,
    ListDataProtectionSettingsResponseTypeDef,
    ListSessionsRequestPaginateTypeDef,
    ListSessionsResponseTypeDef,
)

if sys.version_info >= (3, 12):
    from typing import Unpack
else:
    from typing_extensions import Unpack


__all__ = ("ListDataProtectionSettingsPaginator", "ListSessionsPaginator")


if TYPE_CHECKING:
    _ListDataProtectionSettingsPaginatorBase = Paginator[ListDataProtectionSettingsResponseTypeDef]
else:
    _ListDataProtectionSettingsPaginatorBase = Paginator  # type: ignore[assignment]


class ListDataProtectionSettingsPaginator(_ListDataProtectionSettingsPaginatorBase):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/workspaces-web/paginator/ListDataProtectionSettings.html#WorkSpacesWeb.Paginator.ListDataProtectionSettings)
    [Show types-boto3-full documentation](https://youtype.github.io/types_boto3_docs/types_boto3_workspaces_web/paginators/#listdataprotectionsettingspaginator)
    """

    def paginate(  # type: ignore[override]
        self, **kwargs: Unpack[ListDataProtectionSettingsRequestPaginateTypeDef]
    ) -> PageIterator[ListDataProtectionSettingsResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/workspaces-web/paginator/ListDataProtectionSettings.html#WorkSpacesWeb.Paginator.ListDataProtectionSettings.paginate)
        [Show types-boto3-full documentation](https://youtype.github.io/types_boto3_docs/types_boto3_workspaces_web/paginators/#listdataprotectionsettingspaginator)
        """


if TYPE_CHECKING:
    _ListSessionsPaginatorBase = Paginator[ListSessionsResponseTypeDef]
else:
    _ListSessionsPaginatorBase = Paginator  # type: ignore[assignment]


class ListSessionsPaginator(_ListSessionsPaginatorBase):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/workspaces-web/paginator/ListSessions.html#WorkSpacesWeb.Paginator.ListSessions)
    [Show types-boto3-full documentation](https://youtype.github.io/types_boto3_docs/types_boto3_workspaces_web/paginators/#listsessionspaginator)
    """

    def paginate(  # type: ignore[override]
        self, **kwargs: Unpack[ListSessionsRequestPaginateTypeDef]
    ) -> PageIterator[ListSessionsResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/workspaces-web/paginator/ListSessions.html#WorkSpacesWeb.Paginator.ListSessions.paginate)
        [Show types-boto3-full documentation](https://youtype.github.io/types_boto3_docs/types_boto3_workspaces_web/paginators/#listsessionspaginator)
        """
