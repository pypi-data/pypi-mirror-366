from datetime import datetime, timezone
from pydantic import BaseModel, field_validator, Field
from typing import Any, Literal, TypeVar, Optional, Generic

T = TypeVar("T")


class ErrorPayloadData(BaseModel):
    type: str
    msg: str

class Payload(BaseModel):
    ...

class ErrorPayload(Payload):
    success: Literal[False]
    data: None
    error: ErrorPayloadData

class SuccessPayload(Payload, Generic[T]):
    success: Literal[True]
    data: T
    error: None

class ResponseMeta(BaseModel):
    """
    Optional metadata wrapper included with all API responses.

    This object captures non-payload metadata such as request info, timing,
    versioning, and identifiers. It is included in both success and error
    responses to support observability, traceability, and extensibility.

    Attributes:
        - duration (Optional[float]): Total request duration in milliseconds or seconds.
        - method (Optional[str]): HTTP method (e.g., "GET", "POST"). Automatically normalized to uppercase.
        - path (Optional[str]): Request path or endpoint.
        - request_id (Optional[str]): Unique request identifier for tracing or correlation.
        - timestamp (Optional[datetime]): Time the response was generated. Defaults to current UTC time.
        - version (Optional[str]): API or schema version identifier.
        - extra (Optional[dict[str, Any]]): Arbitrary metadata extensions.
            Use this to include custom keys such as model names, debug flags,
            client platform, or any application-specific meta fields.
    """
    duration: Optional[float] = None
    extra: Optional[dict[str, Any]] = None
    method: Optional[str] = None
    path: Optional[str] = None
    request_id: Optional[str] = None
    timestamp: Optional[datetime] = Field(default_factory=lambda: datetime.now(tz=timezone.utc))
    version: Optional[str] = None

    @field_validator("method")
    @classmethod
    def normalize_method(cls, v: str | None) -> str | None:
        if isinstance(v, str):
            return v.upper()
        return v

class ApiResponse(BaseModel):
    status: int
    meta: ResponseMeta = Field(default_factory=lambda: ResponseMeta())
    
class ApiSuccessResponse(ApiResponse, Generic[T]):
    payload: SuccessPayload[T]

class ApiErrorResponse(ApiResponse):
    payload: ErrorPayload
