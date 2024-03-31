from django import forms
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.views import View
from htmx_view import HTMXViewMixin, register_htmx_view
from render_block import render_block_to_string

from todo.models import TodoItem


class TodoCreateForm(forms.Form):
    title = forms.CharField()


class TodoView(HTMXViewMixin, View):
    template_name = "todo/todo.html"

    def get(self, request: HttpRequest) -> HttpResponse:
        all_todos = TodoItem.objects.all()
        return render(
            request=request,
            template_name=self.template_name,
            context={
                "form": TodoCreateForm(),
                "todos": all_todos,
            },
        )

    @register_htmx_view(method="POST")
    def hx_create(self, request: HttpRequest) -> HttpResponse:
        def form_error_response(*, form: TodoCreateForm) -> HttpResponse:
            response = HttpResponse(
                render_block_to_string(
                    template_name=self.template_name,
                    block_name="form",
                    request=request,
                    context={"form": form},
                )
            )
            response["HX-Retarget"] = "this"
            response["HX-Reswap"] = "outerHTML"
            return response

        form = TodoCreateForm(request.POST)
        if not form.is_valid():
            return form_error_response(form=form)

        title = form.cleaned_data["title"]
        if title == "error":
            form.add_error(field="title", error="This is an error!")
            return form_error_response(form=form)

        new_todo = TodoItem.objects.create(title=title)
        return render(
            template_name="todo/todo_item.html",
            request=request,
            context={"todo": new_todo},
        )

    @register_htmx_view(method="POST")
    def hx_toggle(self, request: HttpRequest, todo_id: int) -> HttpResponse:
        todo = get_object_or_404(TodoItem, id=todo_id)
        todo.is_done = not todo.is_done
        todo.save()
        return render(
            request=request,
            template_name="todo/todo_item.html",
            context={"todo": todo},
        )

    @register_htmx_view(method="POST")
    def hx_delete(self, _request: HttpRequest, todo_id: int) -> HttpResponse:
        todo = get_object_or_404(TodoItem, id=todo_id)
        todo.is_done = not todo.is_done
        todo.delete()
        return HttpResponse("", status=204)
