"""Recallio API client package."""

from .client import RecallioClient
from .models import (
    MemoryWriteRequest,
    MemoryRecallRequest,
    MemoryDeleteRequest,
    MemoryDto,
    MemoryWithScoreDto,
    RecallSummaryRequest,
    SummarizedMemoriesDto,
    GraphAddRequest,
    GraphSearchRequest,
    GraphSearchResult,
    GraphEntity,
    GraphRelationship,
    GraphAddResponse,
    MemoryExportRequest,
    ErrorReturnClass,
)
from .errors import RecallioAPIError

__all__ = [
    "RecallioClient",
    "MemoryWriteRequest",
    "MemoryRecallRequest",
    "MemoryDeleteRequest",
    "MemoryDto",
    "MemoryWithScoreDto",
    "RecallSummaryRequest",
    "SummarizedMemoriesDto",
    "GraphAddRequest",
    "GraphSearchRequest",
    "GraphSearchResult",
    "GraphEntity",
    "GraphRelationship",
    "GraphAddResponse",
    "MemoryExportRequest",
    "ErrorReturnClass",
    "RecallioAPIError",
]
