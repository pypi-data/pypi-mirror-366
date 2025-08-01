from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Generic, TypeVar
from .errors import (
    ApiPayloadBuilderError, 
    ApiResponseBuilderError
)
from .schemas import (
    Payload, 
    SuccessPayload, 
    ErrorPayload, 
    ErrorPayloadData, 
    ApiResponse, 
    ApiSuccessResponse, 
    ApiErrorResponse, 
    ResponseMeta
)

T = TypeVar("T")
P = TypeVar("P", bound=Payload)

class ApiResponseBuilder(ABC, Generic[P]):
    """
    Abstract base class for building fully structured API responses.

    This class coordinates the construction of an `ApiResponse` object,
    including payload generation and response wrapping. Subclasses should
    implement the payload and response construction logic specific to 
    success or error responses.

    Type Parameters:
        P: A concrete subclass of `Payload` (e.g. `SuccessPayload[T]` or `ErrorPayload`).
    """
    def __init__(self, meta: ResponseMeta | None = None):
        if isinstance(meta, ResponseMeta):
            self.meta = meta
        elif meta is None:
            self.meta = ResponseMeta()
        else:
            raise ApiResponseBuilderError(f"Invalid meta argument type: {type(meta)}")

    @staticmethod
    def assert_one_of(data: object | None, error: Exception | None) -> None:
        if data is None and isinstance(error, Exception):
            return
        elif data is not None and error is None:
            return
        else:
            msg = (
                f"Failed to build API response object. Either data "
                f"OR error must be None. data type`{type(data)}`, error type`{type(error)}`"
            )
            raise ApiResponseBuilderError(msg)

    @abstractmethod
    def build(self) -> ApiResponse:
        pass
    
    @abstractmethod
    def _build_response(self, payload: P) -> ApiResponse:
        pass
        
    @abstractmethod
    def _build_payload(self,) -> Payload:
        pass


class ApiSuccessResponseBuilder(ApiResponseBuilder[SuccessPayload[T]], Generic[T]):
    """
    Builder for successful API responses.

    Wraps a data object into a `SuccessPayload`, and then into an
    `ApiSuccessResponse`, including optional metadata and HTTP status.

    Type Parameters:
        T: The type of the object being returned in the response payload.
    """
    def __init__(
            self, 
            data: T, 
            status: int = 200,
            meta: ResponseMeta | None = None,
    ):
        self.data = data
        self.status = status
        super().__init__(meta=meta)

    def build(self) -> ApiSuccessResponse[T]:
        payload = self._build_payload()
        return self._build_response(payload)

    def _build_payload(self) -> SuccessPayload[T]:
        payload_builder = SuccessPayloadBuilder(data=self.data)
        return payload_builder.build_payload()    

    def _build_response(self, payload: SuccessPayload[T]) -> ApiSuccessResponse[T]:
        try:
            api_response = ApiSuccessResponse(
                payload=payload,
                status=self.status,
                meta=self.meta,
            ) 
        except Exception as e:
            msg = f"Failed to build ApiSuccessResponse object due to an unexpected error: {e.__class__.__name__}"
            raise ApiResponseBuilderError(msg) from e
        else:
            return api_response


class ApiErrorResponseBuilder(ApiResponseBuilder[ErrorPayload]):
    """
    Builder for error API responses.

    Converts an exception into a structured `ErrorPayload`, and then
    wraps it in an `ApiErrorResponse`, optionally including response metadata.
    """
    def __init__(
            self,
            error: Exception,
            status: int,
            meta: ResponseMeta | None = None,
    ):
        self.error = error
        self.status = status
        super().__init__(meta=meta)

    def build(self) -> ApiErrorResponse:
        payload = self._build_payload()
        return self._build_response(payload)

    def _build_payload(self) -> ErrorPayload:
        payload_builder = ErrorPayloadBuilder(error=self.error)
        return payload_builder.build_payload()
    
    def _build_response(self, payload: ErrorPayload) -> ApiErrorResponse:
        try:
            api_response = ApiErrorResponse(
                payload=payload,
                status=self.status,
                meta=self.meta,
            ) 
        except Exception as e:
            msg = f"Failed to build ApiErrorResponse object due to an unexpected error: {e.__class__.__name__}"
            raise ApiResponseBuilderError(msg) from e
        else:
            return api_response


class ApiPayloadBuilder(ABC):
    """
    Abstract base class for constructing response payloads.

    Subclasses must implement `build_payload()` to return either
    a `SuccessPayload` or `ErrorPayload` depending on context.
    """
    success: bool
    # data = None
    # _error = None

    @abstractmethod
    def build_payload(self) -> Payload:
        pass


class SuccessPayloadBuilder(ApiPayloadBuilder, Generic[T]):
    """
    Constructs a `SuccessPayload` object from a given data object.

    Type Parameters:
        T: The type of the object included in the payload's `data` field.
    """
    
    success = True
    error = None 
    
    def __init__(self, data: T):
        if data is not None:
            self.data: T = data  # annotating T satisfies mypy
        else:
            msg = f"{self.__class__.__name__} constructor received invalid data argument: `{data}`"
            raise ApiPayloadBuilderError(msg)

    def build_payload(self) -> SuccessPayload[T]:
        try:
            payload = SuccessPayload(success=True, data=self.data, error=None)
        except Exception as e:
            msg = (
                f"{self.__class__.__name__}.build_payload() failed due to an "
                f"unexpected error: `{e.__class__.__name__}`"
            )
            raise ApiPayloadBuilderError(msg) from e

        return payload


class ErrorPayloadBuilder(ApiPayloadBuilder):
    """
    Constructs an `ErrorPayload` object from an exception instance.

    Extracts exception details and serializes them into a standardized
    error payload format.
    """
    
    success = False
    data = None

    def __init__(self, error: Exception):
        if isinstance(error, Exception):
            self.error: Exception = error
        else:
            msg = f"{self.__class__.__name__} constructor received invalid error argument: `{error}`"
            raise ApiPayloadBuilderError(msg)
      
    def build_payload(self) -> ErrorPayload:
        try:
            error = self._build_error_payload_data()
            payload = ErrorPayload(success=False, data=None, error=error)
        except Exception as e:
            msg = (
                f"{self.__class__.__name__}.build_payload() failed due to an "
                f"unexpected error: `{e.__class__.__name__}`"
            )
            raise ApiPayloadBuilderError(msg) from e

        return payload

    def _build_error_payload_data(self) -> ErrorPayloadData:
        error_payload = ErrorPayloadData(
            type=self.error.__class__.__name__,
            msg=str(self.error),
        )

        return error_payload
