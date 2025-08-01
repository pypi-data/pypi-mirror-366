from datetime import datetime, timezone
import pytest
import time        
import json
from typed_api_response.schemas import ResponseMeta, SuccessPayload, ApiSuccessResponse
from typed_api_response.response import build_api_response
from .testdata_cart import cart_dataclass, cart_pydantic


def test_wraps_dataclass():
    
    response = build_api_response(data=cart_dataclass, status=200)
    assert response.status == 200
    assert isinstance(response, ApiSuccessResponse)
    assert isinstance(response.meta, ResponseMeta)    
    assert isinstance(response.payload, SuccessPayload)
    assert response.payload.success == True
    assert response.payload.data == cart_dataclass
    assert response.payload.error == None

def test_wraps_pydantic_model():
    
    response = build_api_response(data=cart_pydantic, status=204)
    assert response.status == 204
    assert isinstance(response, ApiSuccessResponse)
    assert isinstance(response.meta, ResponseMeta)    
    assert isinstance(response.payload, SuccessPayload)
    assert response.payload.success == True
    assert response.payload.data == cart_pydantic
    assert response.payload.error == None

def test_meta_fields_are_preserved():
    before = datetime.now(tz=timezone.utc)
    time.sleep(0.1)

    meta = ResponseMeta(
        duration=3.14,
        extra={"debug": True, "color": "Blue", "foo": "barr"},
        method="get",
        path="/api/foo/bar",
        request_id="1234567890",
        version="1.2.4",
    )

    time.sleep(0.1)
    after = datetime.now(tz=timezone.utc)

    response = build_api_response(data=cart_dataclass, status=202, meta=meta)
    response.meta

    assert isinstance(response.meta, ResponseMeta)
    assert response.meta.method == "GET"
    assert response.meta.version == "1.2.4"
    assert response.meta.request_id == "1234567890"
    assert response.meta.path == "/api/foo/bar"
    assert response.meta.duration == 3.14
    assert response.meta.extra == {"debug": True, "color": "Blue", "foo": "barr"}
    assert response.meta.timestamp is not None
    assert before < response.meta.timestamp < after
        
def test_wraps_without_meta():
    data = cart_pydantic
    response = build_api_response(data=data, status=200)
    if response.meta is not None:
        assert isinstance(response.meta.timestamp, datetime)
        assert response.meta.method is None
        assert response.meta.extra is None
    else:
        pytest.fail("ResponseMeta should not be None!")

def test_payload_is_json_serializable():
    response = build_api_response(data=cart_pydantic, status=200)
    try:
        json.dumps(response.model_dump(mode="json"))
    except TypeError as e:
        pytest.fail(f"Response was not JSON serializable: {e}")