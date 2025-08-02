"""API helper utilities for common operations.

This module provides compatibility imports for backward compatibility.
The actual implementations are now in aceiot_models.api.
"""

import logging
from typing import Any, TypeVar

# Import from upstream aceiot_models
from aceiot_models.api import (
    APIClient,
    batch_process,
    convert_api_response_to_points,
    convert_samples_to_models,
    get_api_results_paginated,
    process_points_from_api,
)

logger = logging.getLogger(__name__)

T = TypeVar("T")

# Re-export for backward compatibility
__all__ = [
    "APIClient",
    "batch_process",
    "convert_api_response_to_points",
    "convert_samples_to_models",
    "get_api_results_paginated",
    "process_points_from_api",
    "post_to_api",
]


def post_to_api(
    client: APIClient,
    endpoint: str,
    data: dict[str, Any],
    params: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Generic POST helper for API operations.

    Args:
        client: APIClient instance
        endpoint: API endpoint to call
        data: Data to POST
        params: Query parameters

    Returns:
        API response dictionary
    """
    return client._request("POST", endpoint, data=data, params=params)
