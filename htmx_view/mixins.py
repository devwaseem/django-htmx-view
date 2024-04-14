import inspect
from typing import Any, Callable, NamedTuple, Type, TypeVar
from uuid import UUID

from django.http import HttpRequest, HttpResponse
from django.urls import URLPattern
from django.urls import path as django_path
from django.views import View

T = TypeVar("T", bound=View)


class UrlParameter(NamedTuple):
    name: str
    annotation: str

    def build_url_param(self) -> str:
        return f"<{self.annotation}:{self.name}>"


class HTMXViewMixin:
    # this is only added to bypass the as_view check
    hx_method_name: str | None = None

    def dispatch(self: View, request: HttpRequest, *args: Any, **kwargs: Any):  # type: ignore # noqa
        if self.hx_method_name:
            resolved_method_name = "hx_" + self.hx_method_name
            if hasattr(self, resolved_method_name):
                handler = getattr(self, resolved_method_name)
                return handler(request, *args, **kwargs)
        return super().dispatch(request, *args, **kwargs)  # type: ignore

    @classmethod
    def htmx_urls(  # type: ignore
        cls: Type[T],
        path: str,
        name: str,
        reverse_url_seperator: str = "->",
        **initkwargs: Any,  # noqa
    ) -> list[URLPattern]:
        # get methods that starts with hx_
        method_name_list: list[str] = [
            attr
            for attr in dir(cls)
            if callable(getattr(cls, attr)) and attr.startswith("hx_")
        ]

        urls = []

        for method_name in method_name_list:
            method_parameters = inspect.signature(
                getattr(cls, method_name)
            ).parameters

            cleaned_method_name = method_name.replace("hx_", "")

            path_suffix = cleaned_method_name + "/"

            # if path does not end with /, then we need to add manually
            # eg: /hello -> /hello/welcome where welcome is the action/method
            if not path.endswith("/"):
                path_suffix = "/" + path_suffix

            skip_params = {"self", "request", "_request"}
            url_params = []

            for param_name, signature in method_parameters.items():
                if param_name in skip_params:
                    continue

                url_param_type = "str"
                if signature.annotation == type(int):
                    url_param_type = "int"
                if signature.annotation == type(UUID):
                    url_param_type = "uuid"

                url_params.append(
                    UrlParameter(
                        name=param_name,
                        annotation=url_param_type,
                    )
                )

            if url_params:
                path_suffix += "/".join(
                    [u.build_url_param() for u in url_params]
                )
                path_suffix += "/"

            url_name = name + reverse_url_seperator + cleaned_method_name

            def get_view(method_name: str) -> Callable[..., HttpResponse]:  # type: ignore
                return cls.as_view(**initkwargs, hx_method_name=method_name)  # type: ignore

            urls.append(
                django_path(
                    path + path_suffix,
                    get_view(cleaned_method_name),
                    name=url_name,
                )
            )

        return urls
