from django.urls import path

from todo.views import TodoView

urlpatterns = [
    path("", TodoView.as_view(), name="todo"),
]

urlpatterns += TodoView().htmx_urls(path="todos", name="todo")
