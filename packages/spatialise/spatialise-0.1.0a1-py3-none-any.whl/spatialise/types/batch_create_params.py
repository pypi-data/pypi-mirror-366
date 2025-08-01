# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Iterable, Optional
from typing_extensions import Literal, Required, Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["BatchCreateParams", "Job", "JobPolygon"]


class BatchCreateParams(TypedDict, total=False):
    jobs: Required[Iterable[Job]]

    metadata: Optional[Dict[str, object]]
    """Optional client-defined metadata"""

    webhook_url: Optional[str]
    """Optional webhook URL for notification"""

    idempotency_key: Annotated[str, PropertyInfo(alias="Idempotency-Key")]
    """Unique key to ensure idempotent request processing"""

    webhook_secret: Annotated[str, PropertyInfo(alias="Webhook-Secret")]
    """Secret token for authenticating webhook callbacks"""


class JobPolygon(TypedDict, total=False):
    coordinates: Required[Iterable[Iterable[Iterable[float]]]]

    type: Required[Literal["Polygon"]]


class Job(TypedDict, total=False):
    polygon: Required[JobPolygon]
    """Geographic area for prediction"""

    year: Required[int]
    """Year for prediction"""
