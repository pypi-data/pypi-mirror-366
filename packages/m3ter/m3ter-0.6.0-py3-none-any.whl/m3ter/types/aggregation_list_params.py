# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List
from typing_extensions import Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["AggregationListParams"]


class AggregationListParams(TypedDict, total=False):
    org_id: Annotated[str, PropertyInfo(alias="orgId")]

    codes: List[str]
    """List of Aggregation codes to retrieve.

    These are unique short codes to identify each Aggregation.
    """

    ids: List[str]
    """List of Aggregation IDs to retrieve."""

    next_token: Annotated[str, PropertyInfo(alias="nextToken")]
    """`nextToken` for multi-page retrievals."""

    page_size: Annotated[int, PropertyInfo(alias="pageSize")]
    """Number of Aggregations to retrieve per page."""

    product_id: Annotated[List[str], PropertyInfo(alias="productId")]
    """The UUIDs of the Products to retrieve Aggregations for."""
