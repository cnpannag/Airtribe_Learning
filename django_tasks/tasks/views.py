from typing import override

from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.viewsets import ViewSet

from .models import Task
from .serializer import TaskSerializer

# Create your views here.
# a view is a function that takes a request and returns a response


@api_view(["GET"])  # This is how Django differentiates this from a regular function
def hello_world(request):
    # returns a response object
    return Response({"message": "Hello, World!"})

@api_view(["GET"])
def add_numbers(request):
    # get the query params
    a = int(request.query_params.get("a"))
    b = int(request.query_params.get("b"))
    return Response({"message": f"{a} + {b} = {a + b}"})
# http://127.0.0.1:8001/api/add-numbers/?a=1&b=2
#  "message": "1 + 2 = 3"

# ******* Tasks - File Reading *******
import json

@api_view(["GET"])
def get_all_tasks(request):
    with open("tasks/files/tasks.json","r") as file:
        tasks=json.loads(file.read())
        # Return the tasks
        return Response(tasks)

@api_view(["GET"])
def get_tasks_by_id(request, id):
    with open("tasks/files/tasks.json","r") as file:
        tasks=json.loads(file.read())
        for task in tasks:
            if task["id"]==id:
                return Response(task)
        # Return the tasks
        return Response("id not found", status=404)


@api_view(["POST"])
def create_task(request):
    with open("tasks/files/tasks.json","r") as file:
        tasks=json.loads(file.read())
        # Create a new task
    task={
        "id": len(tasks)+1,
        "title": request.data.get("title"),
        "description": request.data.get("description"),
        "completed": False
    }
    with open("tasks/files/tasks.json","w") as file:
        tasks.append(task)
        json.dump(tasks, file)
    
    return Response(task, status=201)


def _get_all_tasks():
        with open("tasks/files/tasks.json","r") as file:
            tasks=json.loads(file.read())
            return tasks






#************** another way to do the above **************************************** 

class TaskView(APIView): # APIView is a class that helps us to create a view that can be used in the urls.py file
        # This comes from the rest_framework.views import APIView
        def post(self, request):
            data=request.data
            tasks=_get_all_tasks()
        # Create a new task
            task={
                "id": len(tasks)+1,
                "title": request.data.get("title"),
                "description": request.data.get("description"),
                "completed": False
            }
            with open("tasks/files/tasks.json","w") as file:
                tasks.append(task)
                json.dump(tasks, file)
                return Response(task, status=201)
# post 127.0.0.1:8001/api/create-task-api/
# {
#     "title": "Task 5",
#     "description": "created with TaskView"
# }
# returns the task created
# {
# 	"id": 5,
# 	"title": "Task 5",
# 	"description": "created with TaskView",
# 	"completed": false
# }
        def get(self, request):
            tasks=_get_all_tasks()
            return Response(tasks)
        # The above GET will not work because it will take the below one
        # to fix this we have added another condition in the below get if id is none

        def get(self, request, id):
            tasks=_get_all_tasks()
            if id is None:
                return Response(tasks)
            for task in tasks:
                if task["id"]==id:
                    return Response(task)
            return Response("id not found", status=404)
        
        def delete(self, request, id):
            tasks=_get_all_tasks()
            for task in tasks:
                if task["id"]==id:
                    tasks.remove(task)
                    with open("tasks/files/tasks.json","w") as file:
                        json.dump(tasks, file)
                    return Response("task deleted", status=204)
            return Response("id not found", status=404)


# class TaskViewSet(ViewSet):
#     # queryset = Task.objects.all()
#     # queryset is basically the DB query that will be executed to get the data
#     # serializer_class = TaskSerializer
#     # serializer_class is the serializer that will be used to serialize the data.

#     @override
#     def list(self, request):  # GET request to get all tasks
#         tasks = Task.objects.all()
#         serializer = TaskSerializer(tasks, many=True)  # many=True is used because there are multiple tasks
#         return Response(serializer.data)

#     @override
#     def retrieve(self, request, pk=None):  # GET request to get a task by id. pk is the primary key
#         try:
#             task = Task.objects.get(id=pk)
#             serializer = TaskSerializer(task)
#             return Response(serializer.data)
#         except Task.DoesNotExist:
#             return Response(
#                 {"error": "Task not found"}, status=status.HTTP_404_NOT_FOUND
#             )

#     @override
#     def create(self, request):  # POST request to create a new task
#         serializer = TaskSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#     @override
#     def update(self, request, pk=None):  # PUT request to update a task
#         try:
#             task = Task.objects.get(id=pk)
#             serializer = TaskSerializer(task, data=request.data)
#             if serializer.is_valid():
#                 serializer.save()
#                 return Response(serializer.data, status=status.HTTP_200_OK)
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#         except Task.DoesNotExist:
#             return Response(
#                 {"error": "Task not found"}, status=status.HTTP_404_NOT_FOUND
#             )

#     @override
#     def destroy(self, request, pk=None):  # DELETE request to delete a task
#         try:
#             task = Task.objects.get(id=pk)
#             task.delete()
#             return Response(status=status.HTTP_204_NO_CONTENT)
#         except Task.DoesNotExist:
#             return Response(
#                 {"error": "Task not found"}, status=status.HTTP_404_NOT_FOUND
#             )

#     @override
#     def partial_update(self, request, pk=None):  # PATCH request to partially update a task
#         try:
#             task = Task.objects.get(id=pk)
#             serializer = TaskSerializer(task, data=request.data, partial=True)
#             if serializer.is_valid():
#                 serializer.save()
#                 return Response(serializer.data, status=status.HTTP_200_OK)
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#         except Task.DoesNotExist:
#             return Response(
#                 {"error": "Task not found"}, status=status.HTTP_404_NOT_FOUND
#             )



from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
# The whole above one can be simply replaces by the following using modelviewset:
class TaskViewSet(ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

    # this will add on to what is already present in the ModelViewSet 

    @action(detail=False, methods=["get"])
    def get_incomplete_tasks(self, request):
        tasks = Task.objects.filter(completed=False)
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)
        # api for this will be 127.0.0.1:8001/api/tasks/get-incomplete-tasks/

        # detail=False means that the action is not associated with a specific task.
        # detail=True means that the action is associated with a specific task.
    # @action(detail=True, methods=["get"])
    @action(detail=True, methods=["get"], url_path="get-a-specific-task")
    def get_a_specific_task(self, request, pk=None): #pk can be taken here because we have detail=True in the action decorator
        task = Task.objects.get(id=pk) 
        serializer = TaskSerializer(task)
        return Response(serializer.data)
        # api for this will be 127.0.0.1:8001/api/tasks/1/get-a-specific-task/


# ModelViewSet can be used when we are using a model and we want to create a viewset for it.
# but when we are not using a model and we want to create a viewset for it, we can use ViewSet.



    
    
        
        
