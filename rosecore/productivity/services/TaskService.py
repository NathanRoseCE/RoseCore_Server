from productivity.models.Task import Task
from productivity.models.Project import Project
from django.shortcuts import get_object_or_404
import datetime

from rosecore.productivity.services.TodoistService import TodoistService

class TaskService:
    @staticmethod
    def get_tasks(limit=None):
        return Task.objects.all()[:limit]

    @staticmethod
    def get_task_or_404(task_id):
        return get_object_or_404(Task, pk=task_id)

    @staticmethod
    def createTask(content:str="content",
                   description:str="",
                   project:Project=None,
                   priority:int=3,
                   nextDue:datetime=datetime.today(),
                   **args) -> Task:
        todoistId = args["todoistId"] if "todoistId" in args else ""
        if todoistId:
            TaskService.validateTodoistId(todoistId)
        else:
            #TODO: create task in todoist service
            pass
        raise NotImplemented()


    @staticmethod
    def validateTodoistId(todoistId: str) -> None:
        pass
    
        
