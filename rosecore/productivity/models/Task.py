from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from . import Project


class Task(models.Model):
    id = models.AutoField(primary_key=True)
    content = models.CharField(max_length=50)
    priority = models.IntegerField(
        default=3,
        validators=[
            MaxValueValidator(4),
            MinValueValidator(1)
        ]
    )
    todoistId = models.CharField(max_length=50)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    due = models.DateTimeField()
