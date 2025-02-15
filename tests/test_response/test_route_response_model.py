from typing import List, Union

import pytest
from starlette.responses import JSONResponse

from ellar.core.response.model import (
    EmptyAPIResponseModel,
    JSONResponseModel,
    ResponseModel,
    RouteResponseExecution,
    RouteResponseModel,
)

from ..schema import BlogObjectDTO, NoteSchemaDC


class JsonApiResponse(JSONResponse):
    media_type = "application/vnd.api+json"


class JsonApiResponseModel(ResponseModel):
    response_type = JsonApiResponse


@pytest.mark.parametrize(
    "route_responses, route_model, status, description, content_type",
    [
        (
            {200: List[Union[NoteSchemaDC, BlogObjectDTO]]},
            JSONResponseModel,
            200,
            "Successful Response",
            "application/json",
        ),
        (
            {200: EmptyAPIResponseModel()},
            EmptyAPIResponseModel,
            200,
            "Successful Response",
            "application/json",
        ),
        (
            {
                201: (Union[NoteSchemaDC, BlogObjectDTO], "Create Note"),
                200: EmptyAPIResponseModel(),
            },
            JSONResponseModel,
            201,
            "Create Note",
            "application/json",
        ),
        (
            {
                201: (Union[NoteSchemaDC, BlogObjectDTO], "Create Note"),
                200: EmptyAPIResponseModel(),
            },
            JSONResponseModel,
            200,
            "Successful Response",
            "application/json",
        ),
        (
            {200: JsonApiResponseModel()},
            JsonApiResponseModel,
            200,
            "Successful Response",
            "application/vnd.api+json",
        ),
        (
            {200: JsonApiResponse},
            ResponseModel,
            200,
            "Successful Response",
            "application/vnd.api+json",
        ),
    ],
)
def test_route_response_model(
    route_responses, route_model, status, description, content_type
):
    route_response_model = RouteResponseModel(route_responses=route_responses)
    assert route_response_model.models[status]
    assert route_response_model.models[status].media_type == content_type
    assert route_response_model.models[status].description == description
    assert isinstance(route_response_model.models[status], route_model)


@pytest.mark.parametrize(
    "inputs",
    [
        list(),
        set(),
        tuple(),
        ResponseModel,
        JsonApiResponseModel,
        EmptyAPIResponseModel,
    ],
)
def test_route_response_model_exception(inputs):
    with pytest.raises(RouteResponseExecution):
        RouteResponseModel(route_responses=inputs)
