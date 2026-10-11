from rest_framework import serializers

from .models import Task, User


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ["id", "title", "description", "completed", "created_at", "updated_at", "user"]
        read_only_fields = ["id", "created_at", "updated_at"]

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "first_name", "last_name", "email", "password", "created_at", "updated_at", "is_active"]
        read_only_fields = ["id", "created_at", "updated_at"]
        depth = 1 # this will return the tasks for the user in the response

class TaskUserSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    task_list = TaskSerializer(many=True,read_only=True)