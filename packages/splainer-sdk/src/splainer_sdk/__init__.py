"""Splainer SDK — Python client for SPL-to-SQL translation."""

from splainer_sdk._version import __version__
from splainer_sdk.client import SplainerClient
from splainer_sdk.async_client import AsyncSplainerClient
from splainer_sdk.models import (
    Dialect,
    TranslateResult,
    PipelineStep,
    PipelineDetail,
    ExecutionDetail,
    HealthStatus,
)
from splainer_sdk.exceptions import (
    SplainerError,
    TranslationError,
    ParseError,
    CodegenError,
    ExecutionError,
    ConfigurationError,
    APIError,
)

__all__ = [
    "__version__",
    "SplainerClient",
    "AsyncSplainerClient",
    "Dialect",
    "TranslateResult",
    "PipelineStep",
    "PipelineDetail",
    "ExecutionDetail",
    "HealthStatus",
    "SplainerError",
    "TranslationError",
    "ParseError",
    "CodegenError",
    "ExecutionError",
    "ConfigurationError",
    "APIError",
]

