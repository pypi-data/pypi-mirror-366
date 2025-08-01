from datetime import datetime
import pytest
from typed_api_response.schemas import ResponseMeta, ErrorPayload, ApiErrorResponse, ErrorPayloadData
from typed_api_response.response import build_api_response


class CustomExceptionForTest(Exception):
    pass

def test_error_shape():
    try:
        _ = 1 / 0
    except Exception as e:
        response = build_api_response(error=e, status=418)

        assert response.status == 418
        assert isinstance(response, ApiErrorResponse)
        assert isinstance(response.meta, ResponseMeta)
        assert isinstance(response.payload, ErrorPayload)
        assert isinstance(response.payload.error, ErrorPayloadData)
        assert response.payload.error.type == e.__class__.__name__
        assert response.payload.error.msg == str(e)
        assert response.payload.success == False
        assert response.payload.data == None
    else:
        pytest.fail("How???")

def test_custom_exception():
    try:
        raise CustomExceptionForTest("The app is broken")
    except CustomExceptionForTest as e:
        response = build_api_response(error=e, status=500)
        assert response.payload.error.type == "CustomExceptionForTest"
        assert response.payload.error.msg == "The app is broken"
        
def test_error_with_custom_meta():
    meta = ResponseMeta(method="post", path="/fail")
    try:
        raise RuntimeError("bad things")
    except Exception as e:
        response = build_api_response(error=e, status=500, meta=meta)

        assert response.meta is not None
        assert isinstance(response.meta, ResponseMeta)
        assert response.meta.method == "POST"
        assert response.meta.path == "/fail"
        assert response.payload.error.type == e.__class__.__name__
        assert response.payload.error.msg == str(e)
        assert response.payload.success == False
        assert response.payload.data == None
    else:
        pytest.fail("No error raised. Did you change error behavior?")

def test_timestamp_is_set():
    foo = [1, 2, 3, 4]
    try:
        foo[9999]
    except IndexError as e:
        response = build_api_response(error=e, status=404)
        assert response.meta is not None
        assert response.meta.timestamp is not None
        assert isinstance(response.meta.timestamp, datetime) 
    else:
        pytest.fail("No error raised. Did you change error behavior?")