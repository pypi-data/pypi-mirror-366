"""Utilities package for aceiot-models-cli."""

# Import from upstream aceiot_models.api for backward compatibility
from aceiot_models.api import (
    PaginatedResults,
    batch_process,
    convert_api_response_to_points,
    convert_samples_to_models,
    get_api_results_paginated,
    process_points_from_api,
)

# Import CLI-specific utilities that are not in upstream
from .api_helpers import post_to_api

__all__ = [
    "get_api_results_paginated",
    "post_to_api",
    "batch_process",
    "process_points_from_api",
    "convert_api_response_to_points",
    "convert_samples_to_models",
    "PaginatedResults",
]
