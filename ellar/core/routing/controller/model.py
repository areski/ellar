import typing as t

from ellar.core.context import ExecutionContext


class ControllerType(type):
    _controller_name: t.Optional[str]

    @t.no_type_check
    def __new__(mcls, name, bases, namespace, **kwargs):
        cls = super().__new__(mcls, name, bases, namespace, **kwargs)
        cls._controller_name = None
        return cls

    def controller_class_name(cls) -> str:
        """ """
        if cls._controller_name:
            return cls._controller_name
        return cls.__name__.lower().replace("controller", "")

    def full_view_name(cls, name: str) -> str:
        """ """
        return f"{cls.controller_class_name()}/{name}"


class ControllerBase(metaclass=ControllerType):
    # `context` variable will change based on the route function called on the APIController
    # that way we can get some specific items things that belong the route function during execution
    context: t.Optional[ExecutionContext] = None
