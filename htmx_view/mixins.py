import inspect
from typing import Callable, NamedTuple
from uuid import UUID

from django.http import HttpResponse
from django.urls import URLPattern
from django.urls import path as django_path


class UrlParameter(NamedTuple):
    name: str
    annotation: str

    def build_url_param(self) -> str:
        return f"<{self.annotation}:{self.name}>"


class HTMXViewMixin:
    @classmethod
    def htmx_urls(
        cls,
        path: str,
        name: str,
        reverse_url_seperator="->",
        **initkwargs,
    ) -> list[URLPattern]:
        # get methods that starts with hx_
        actions: list[str] = [
            attr
            for attr in dir(cls)
            if callable(getattr(cls, attr)) and attr.startswith("hx_")
        ]

        urls = []

        for attr in actions:
            method_name = attr.replace("hx_", "")

            path_suffix = method_name + "/"

            # if path does not end with /, then we need to add manually
            # eg: /hello -> /hello/welcome where welcome is the action/method
            if not path.endswith("/"):
                path_suffix = "/" + path_suffix

            method_parameters = inspect.signature(
                getattr(cls, attr)
            ).parameters

            skip_params = {"self", "request"}
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

            url_name = name + reverse_url_seperator + method_name

            def get_view(attr: str) -> Callable[..., HttpResponse]:  # type: ignore
                self = cls(**initkwargs)
                return getattr(self, attr)  # type: ignore

            urls.append(
                django_path(
                    path + path_suffix,
                    get_view(attr),
                    name=url_name,
                )
            )

        return urls
