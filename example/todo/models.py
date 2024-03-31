from django.db import models

# Create your models here.


class TodoItem(models.Model):
    title = models.CharField(max_length=255)
    is_done = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.title
