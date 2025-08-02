# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List
from typing_extensions import Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["CreditReasonListParams"]


class CreditReasonListParams(TypedDict, total=False):
    org_id: Annotated[str, PropertyInfo(alias="orgId")]

    archived: bool
    """TRUE / FALSE archived flag to filter the list.

    CreditReasons can be archived once they are obsolete.

    - TRUE includes archived CreditReasons.
    - FALSE excludes CreditReasons that are archived.
    """

    codes: List[str]
    """List of Credit Reason short codes to retrieve."""

    ids: List[str]
    """List of Credit Reason IDs to retrieve."""

    next_token: Annotated[str, PropertyInfo(alias="nextToken")]
    """`nextToken` for multi page retrievals."""

    page_size: Annotated[int, PropertyInfo(alias="pageSize")]
    """Number of credit reasons to retrieve per page."""
