from functools import wraps
from typing import Callable, Literal, TypeVar

from django.http import HttpRequest, HttpResponse
from django.views import View

T = TypeVar("T", bound=View)


def register_htmx_view(  # type: ignore
    *,
    method: Literal["GET", "POST"],
) -> Callable[[Callable[..., HttpResponse]], Callable[..., HttpResponse]]:
    def decorator(  # type: ignore
        action_function: Callable[..., HttpResponse],
    ) -> Callable[..., HttpResponse]:
        @wraps(action_function)
        def wrap(
            self: T,
            request: HttpRequest,
            *args: object,
            **kwargs: object,
        ) -> HttpResponse:
            if request.method != method:
                return HttpResponse("", status=405)
            return action_function(self, request, *args, **kwargs)

        return wrap

    return decorator
