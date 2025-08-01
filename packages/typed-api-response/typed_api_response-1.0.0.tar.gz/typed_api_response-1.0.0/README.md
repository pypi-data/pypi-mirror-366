# Typed API Response

A unified, type-safe API response format for Python — with full type inference, Pydantic support, and consistent structure for both success and error responses.
Just pass your data or exception — build_api_response() handles the rest.

> Works seamlessly with FastAPI, Django Ninja, or any Pydantic-based Python project.
> Accepts Pydantic models, dataclasses, or any structured object.


## 🧪 Type Safety

This library is:
- Designed for **Pylance** and **mypy strict mode**
- Fully generic — type-safe through all layers
- Uses **overloads** to preserve type inference

No need to type hint manually:

```python
response = build_api_response(data=MySchema(...), status=200)
# response.payload.data is inferred as MySchema ✅
```

➡️ Want proof? [See the typecheck file](tests/typecheck/mypy_typecheck.py)

> This is a static analysis file for `mypy`. It uses `reveal_type()` to confirm that generic types and payload structures are preserved correctly.  
> You can run it with `mypy` or open it in VSCode and hover to inspect types inline — no need to execute the file.


## 🔧 Features

- ✅ Typed response builders for both success and error responses
- ✅ Fully generic, Pylance-compliant with strict mode enabled
- ✅ Single unified function: `build_api_response(...)`
- ✅ Extensible metadata support via `ResponseMeta`
- ✅ Automatically distinguishes between `data` and `error`
- ✅ Raises clean custom exceptions on misconfiguration


## 🚀 Getting Started


### Install with **pip**

```bash
pip install typed-api-response
```


### Define your Pydantic response schema

```python
from pydantic import BaseModel

class MyOutputSchema(BaseModel):
    product_name: str
    description: str
    price: float
    qty: int
    on_sale: bool
```


### Create a typed API response:

```python
@router.post("/foo")
def foo():
    your_data = MyOutputSchema(
      product_name="Big Bag of Rice",
      description="The world's greatest rice ever made. Anywhere. Ever.",
      price=17.99,
      qty=47328,
      on_sale=False,
    )
    response = build_api_response(data=your_data, status=200)
    # response.payload.data is inferred as MyOutputSchema ✅
```

✅ build_api_response() accepts any Pydantic model or well-typed object (e.g. a dataclass) and wraps it into a fully structured, metadata-rich response — with full type hint propagation and IDE support via generics.


### Handling errors just as cleanly

You can also return exceptions using the same unified response format:

```python
try:
    ...
except Exception as e:
    return build_api_response(error=e, status=418)
```

✅ build_api_response() wraps the exception in a type-safe, structured error payload — so your failure responses stay as consistent and predictable as your success ones.


## 🧱 API Structure

### Unified Interface

```python
def build_api_response(
    *,
    data: T | None = None,
    error: Exception | None = None,
    status: int,
    meta: ResponseMeta | None = None,
) -> ApiSuccessResponse[T] | ApiErrorResponse
```

- Provide **either** `data` *or* `error`, not both
- `meta` lets you attach timing, versioning, request ID, etc.
- If neither `data` nor `error` is passed, raises `ApiResponseBuilderError`


### Success Response Format

```json
{
  "status": 200,
  "meta": {
    "duration": null,
    "extra": null,
    "method": null,
    "path": null,
    "request_id": null,
    "timestamp": "2025-07-30T04:33:44.833Z",
    "version": null
  },
  "payload": {
    "success": true,
    "data": {
      "product_name": "Big Bag of Rice",
      "description": "The world's greatest rice ever made. Anywhere. Ever.",
      "price": 17.99,
      "qty": 47328,
      "on_sale": false
    },
    "error": null
  }
}
```


### Error Response Format

```json
{
  "status": 418,
  "meta": {
    "duration": null,
    "extra": null,
    "method": null,
    "path": null,
    "request_id": null,
    "timestamp": "2025-07-30T00:13:55.531Z",
    "version": null
  },
  "payload": {
    "success": false,
    "data": null,
    "error": {
      "type": "ZeroDivisionError",
      "msg": "division by zero"
    }
  }
}
```


## 🧠 Customizing Metadata

Use `ResponseMeta` to attach custom fields:

```python
meta = ResponseMeta(
    request_id="abc123",
    version="v1.2.0",
    extra={"model": "en_streetninja", "debug": True}
)

return build_api_response(data=result, status=200, meta=meta)
```


## 🛡️ Exceptions

This package raises:

- `ApiResponseBuilderError` – if payload generation fails
- `ApiPayloadBuilderError` – if payload data is inconsistent or incomplete


## 📦 Components

- `ApiResponseBuilder` – abstract base class for builders
- `ApiSuccessResponseBuilder` – builds `ApiSuccessResponse[T]`
- `ApiErrorResponseBuilder` – builds `ApiErrorResponse`
- `ResponseMeta` – optional metadata block
- `Payload` / `SuccessPayload[T]` / `ErrorPayload` – structured payload schemas


## ☕ Support This Project

If this saved you time or made your API cleaner, feel free to [buy me a coffee](https://www.buymeacoffee.com/firstflush). Thanks for your support 🙏