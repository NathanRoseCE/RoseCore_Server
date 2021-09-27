from productivity.models import Task
from django.shortcuts import get_object_or_404


class TaskService:
    @staticmethod
    def get_tasks(limit=None, **filters):
        raise NotImplementedError()

    @staticmethod
    def get_project_or_404(task_id):
        return get_object_or_404(Task, pk=task_id)

    @staticmethod
    def createTask(*args):
        raise NotImplementedError()

    @staticmethod
    def completeTask(task: Task):
        raise NotImplementedError()

    @staticmethod
    def deleteTask(task: Task):
        raise NotImplementedError()

    @staticmethod
    def updateTask(task: Task):
        raise NotImplementedError()

    @staticmethod
    def sync():
        """
        This method pulls correct data from Todoist and puts it in the database.
        Todoist is always considered correct
        """
        raise NotImplementedError()
