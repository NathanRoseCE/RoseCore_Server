from django.db import models

# Create your models here.


class Project(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50, unique=True)
    parent = models.ForeignKey('self', blank=True, null=True, related_name='children',
                               on_delete=models.CASCADE)
    todoistId = models.CharField(max_length=50)
    togglId = models.CharField(max_length=50)

    def __str__(self):
        return self.name
