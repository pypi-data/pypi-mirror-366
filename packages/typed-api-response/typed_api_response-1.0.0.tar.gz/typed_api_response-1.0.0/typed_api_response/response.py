from typing import overload, TypeVar
from .errors import ApiResponseBuilderError
from .schemas import ApiSuccessResponse, ApiErrorResponse, ResponseMeta
from .builders import ApiSuccessResponseBuilder, ApiErrorResponseBuilder, ApiResponseBuilder

T = TypeVar("T")

# Overload for success
@overload
def build_api_response(
    *,
    data: T,
    error: None = None,
    status: int,
    meta: ResponseMeta | None = None,
) -> ApiSuccessResponse[T]: ...

# Overload for error
@overload
def build_api_response(
    *,
    data: None = None,
    error: Exception,
    status: int,
    meta: ResponseMeta | None = None,
) -> ApiErrorResponse: ...

def build_api_response(
    *,
    status: int,
    data: T | None = None,
    error: Exception | None = None,
    meta: ResponseMeta | None = None,
) -> ApiSuccessResponse[T] | ApiErrorResponse:
    """
    Constructs a fully structured API response from either data or an error.

    This is the primary entry point for generating standardized API responses.
    It automatically wraps the input into a `SuccessPayload` or `ErrorPayload`
    and returns an `ApiSuccessResponse` or `ApiErrorResponse` accordingly.

    Exactly one of `data` or `error` must be provided.

    Args:
        data (T): The data to include in the success response payload.
        error (Exception): The exception to include in the error response payload.
        status (int): The HTTP status code to attach to the response.
        meta (ResponseMeta | None): Optional metadata to include with the response,
            such as a timestamp or request ID. If not provided, a default will be used.

    Returns:
        ApiSuccessResponse[T]: If `data` is provided.
        ApiErrorResponse: If `error` is provided.

    Raises:
        ApiResponseBuilderError: 
            - If both `data` and `error` are provided, or neither are.
            - If an unexpected error occurs while building the response.
    """
    ApiResponseBuilder.assert_one_of(data=data, error=error)
    try:
        if data:
            return ApiSuccessResponseBuilder(data=data, status=status, meta=meta).build()
        if error:
            return ApiErrorResponseBuilder(error=error, status=status, meta=meta).build()
    except Exception as e:
        msg = f"Failed to build API response object due to an unexpected error: `{e.__class__.__name__}`"
        raise ApiResponseBuilderError(msg) from e
    else:
        raise ApiResponseBuilderError(f"Unable to build API response with data type `{data}` and error type `{error}`")