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
                   nextDue:datetime.datetime=datetime.datetime.now(),
                   commit: bool=False,
                   **args) -> Task:
        todoistId = args["todoistId"] if "todoistId" in args else ""
        if todoistId:
            TaskService.validateTodoistId(todoistId)
        else:
            todoistId = TodoistService.createTask(content=content,
                                                     description=description,
                                                     project_id=Project.todoistId,
                                                     priority=priority,
                                                     due_string=nextDue.strftime('%m/%d/%Y'))
        task = Task(
            content=content,
            description=description,
            project=project,
            priority=priority,
            todoistIdid=todoistId,
            nextDue=nextDue
        )
        if commit:
            task.save()
        return task

    @staticmethod
    def deleteTask(task: Task) -> None:
        """
        Deletes a task, object is no longer valid after being passed
        """
        if (task.todoistId is not None) and (task.todoistId != ""):
            TodoistService.deleteTask(task.todoistId)
        task.delete()

    @staticmethod
    def getTask(id: str) -> Task:
        """
        gets a task by id, uses get_task_or_404 as implimentation
        """
        return TaskService.get_task_or_404(id)

    @staticmethod
    def updateTask(task: Task) -> None:
        """
        Updates a task
        """
        update_data ={}
        update_data["priority"] = task.priority
        update_data["description"] = task.description
        update_data["content"] = task.content
        if task.complete:
            TaskService.markComplete(task)
        TodoistService.updateTask(update_data)
        
    @staticmethod
    def markComplete(task: Task) -> None:
        """
        marks a task as complete
        """
        task.complete = True
        task.save()
        TodoistService.completeTask(task.todoistId)
    
    @staticmethod
    def validateTodoistId(todoistId: str) -> bool:
        """
        validates an id is actually on todoist
        """
        return todoistId in [
            task["id"] for task in TodoistService.getAllTasks()
        ]
