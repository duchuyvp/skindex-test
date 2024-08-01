import dataclasses
import http
import logging
from typing import Callable, List, Any

import httpx
import pydantic
from utils import dictionary

logger = logging.getLogger(__file__)


@dataclasses.dataclass
class ExpectedResponse:

    status_code: http.HTTPStatus = http.HTTPStatus.OK
    headers: dict[str, str] = None
    header_schema: dict[str, type] = None
    body: dict[str, Any] = None
    body_schema: pydantic.BaseModel | list[pydantic.BaseModel] = None

    def __post_init__(self):
        self.body_class: type[pydantic.BaseModel] = self.body_schema.__class__

    def validate(
        self,
        response: httpx.Response,
    ):
        assert response.status_code == self.status_code
        self.validate_headers(response)
        self.validate_body(response)

    def validate_headers(
        self,
        response: httpx.Response,
    ): ...

    def validate_body(
        self,
        response: httpx.Response,
    ):
        if self.body_schema is None:
            return

        if isinstance(self.body_schema, list):
            self.body_schema = pydantic.TypeAdapter(self.body_schema)
            self.body_schema.validate(response.json())
            return
        self.body_schema.model_validate(response.json())
        if self.body is None:
            return
        result, key = dictionary.is_subdict(self.body, response.json())

        assert result
        assert key


def validate_response(
    response: httpx.Response,
    expected_response: ExpectedResponse,
):
    expected_response.validate(response)


Schema = dict[str, Callable[..., Any]]


def validate_is_schema(obj: object):
    if not isinstance(obj, dict):
        raise ValueError(f"Expected a dict, got {type(obj)}")

    for key, value in obj.items():
        if not isinstance(key, str):
            raise ValueError(f"Expected a string key, got {type(key)}")
        if not isinstance(value, Callable):
            raise ValueError(f"Expected a callable value, got {type(value)}")


class TestOrchestrator:

    __test__: bool = False

    def __init__(
        self,
        client: httpx.Client,
        url_factory: dict[str, dict[str, str]],
        request_body_factory: dict[str, Schema],
        default_value_factory: dict[str, dict[str, Any]],
        response_schema_factory: dict[str, pydantic.BaseModel],
    ):
        self.client = client
        self.url_factory = url_factory
        self._request_body_factory = request_body_factory
        self.default_value_factory = default_value_factory
        self.response_schema_factory = response_schema_factory

    @property
    def request_body_factory(self) -> dict[str, Schema]:
        return self._request_body_factory

    @request_body_factory.setter
    def request_body_factory(self, value: dict[str, Schema]):
        validate_is_schema(value)
        self._request_body_factory = value

    def get_url(self, behavior: str) -> tuple[str, str]:
        path, method = self.url_factory[behavior].values()

        return path, method

    def make_request_body(self, behavior: str) -> dict[str, Any]:
        schema = self.request_body_factory[behavior]
        if schema is None:
            return schema
        return {key: value() for key, value in schema.items()}

    def get_response(
        self,
        behavior: str,
        url: str = None,
        method: str = None,
        url_kwargs: dict[str, Any] = None,
        request_body: dict[str, Any] = None,
    ) -> httpx.Response:
        if url is None:
            url, method = self.get_url(behavior)
        if url_kwargs is None:
            url = url.format(**url_kwargs)
        if request_body is None:
            request_body = self.make_request_body(behavior)
        response = self.client.request(
            method=method,
            url=url,
            json=request_body,
        )

        return response

    def make_expected_response(
        self,
        behavior: str = None,
        id: str = None,
        body: dict[str, Any] = None,
        resource: str = None,
        status_code: int | http.HTTPStatus = http.HTTPStatus.OK,
    ) -> ExpectedResponse:
        if isinstance(status_code, int):
            status_code = http.HTTPStatus(status_code)

        if 200 <= status_code.value <= 299:
            if behavior is None:
                raise ValueError("Behavior is required for 2xx status codes")
            if resource is None:
                resource = behavior.split("_")[-1]

            default_values = self.default_value_factory.get(resource)
            if body is None:
                body = {}

            body["id"] = body.get("id", id)
            body_schema = self.response_schema_factory.get(resource)
            response = ExpectedResponse(
                status_code=status_code,
                body_schema=body_schema,
                body=body,
            )

            return response

        return ExpectedResponse(status_code=status_code)
