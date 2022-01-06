from django.db import models

class Task(models.Model):
    id = models.AutoField(primary_key=True)
    content = models.CharField(max_length=100, unique=True)
    description = models.CharField(max_length=100, unique=True)
    project = models.ForeignKey('Project', blank=True, null=True, related_name='Tasks', on_delete=models.CASCADE)
    priority = models.IntegerField()
    todoistId = models.CharField(max_length=50)
    next_due=models.DateTimeField()

    def __str__(self):
        return f"{self.content}({self.due}) - {self.next_due}"
    
