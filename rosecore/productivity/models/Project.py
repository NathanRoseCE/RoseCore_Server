from django.db import models


class Project(models.Model):
    """
    A project is a collection of tasks and time entries under one, user-defined name
    """
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    parent = models.ForeignKey('self', blank=True, null=True, related_name='children',
                               on_delete=models.CASCADE)
    todoistId = models.CharField(max_length=50)
    togglId = models.CharField(max_length=50)
    unsyncedSource = models.CharField(max_length=50,default="") 

    def __str__(self):
        return self.name

    @property
    def synced(self) -> bool:
        return not self.unsyncedSource.strip()

    
