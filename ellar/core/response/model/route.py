import typing as t

from pydantic import BaseModel

from ellar.core.context import IExecutionContext

from ..response_types import Response
from .base import ResponseModel, ResponseResolver, RouteResponseExecution
from .factory import create_response_model
from .interface import IResponseModel
from .json import JSONResponseModel


class RouteResponseModel:
    __slots__ = ("models",)

    def __init__(
        self,
        route_responses: t.Dict[int, t.Union[t.Type, IResponseModel, t.Type[Response]]],
    ) -> None:
        self.models: t.Dict[int, IResponseModel] = {}
        self.convert_route_responses_to_response_models(route_responses)

    def convert_route_responses_to_response_models(
        self,
        route_responses: t.Dict[int, t.Union[t.Type, IResponseModel, t.Type[Response]]],
    ) -> None:
        self.validate_route_response(route_responses)
        for status_code, response_schema in route_responses.items():
            assert (
                isinstance(status_code, int) or status_code == Ellipsis
            ), "status_code must be a number"
            description: str = "Successful Response"
            if isinstance(response_schema, (tuple, list)):
                response_schema, description = response_schema

            if isinstance(response_schema, type) and issubclass(
                response_schema, Response
            ):
                self.models[status_code] = create_response_model(
                    ResponseModel,
                    response_type=response_schema,
                    description=description,
                )
                continue

            if isinstance(response_schema, IResponseModel):
                self.models[status_code] = response_schema
                continue

            self.models[status_code] = create_response_model(
                JSONResponseModel,
                model_field_or_schema=t.cast(t.Type[BaseModel], response_schema),
                description=description,
            )

    def response_resolver(
        self,
        ctx: IExecutionContext,
        endpoint_response_content: t.Union[t.Any, t.Tuple[int, t.Any]],
    ) -> ResponseResolver:
        status_code: int = 200
        response_obj: t.Any = endpoint_response_content

        if len(self.models) == 1:
            status_code = list(self.models.keys())[0]

        if ctx.has_response and ctx.get_response().status_code > 0:
            status_code = ctx.get_response().status_code

        if isinstance(response_obj, tuple) and len(response_obj) == 2:
            status_code, response_obj = endpoint_response_content

        if status_code in self.models:
            response_model = self.models[status_code]
        elif Ellipsis in self.models:
            response_model = self.models[Ellipsis]  # type: ignore
        else:
            raise RouteResponseExecution(
                f"No response Schema with status_code={status_code} in response {self.models.keys()}"
            )
        response_model = t.cast(ResponseModel, response_model)
        return ResponseResolver(status_code, response_model, response_obj)

    def process_response(
        self, ctx: IExecutionContext, response_obj: t.Union[t.Any, t.Tuple[int, t.Any]]
    ) -> Response:
        if isinstance(response_obj, Response):
            return response_obj

        resolver = self.response_resolver(ctx, response_obj)
        return resolver.response_model.create_response(
            status_code=resolver.status_code,
            context=ctx,
            response_obj=resolver.response_object,
        )

    @classmethod
    def validate_route_response(
        cls,
        route_responses: t.Dict[int, t.Union[t.Type, IResponseModel, t.Type[Response]]],
    ) -> None:
        if not isinstance(route_responses, dict):
            raise RouteResponseExecution(
                "Invalid Type. Required type=Union[Type, Dict[int, Type]]"
            )
