from rest_framework import serializers

from .models import IssueSchema, ReporterSchema


class IssueSerializer(serializers.ModelSerializer):
    class Meta:
        model = IssueSchema
        fields = ["id", "title", "description", "status", "priority", "reporter", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]

class ReporterSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReporterSchema
        fields = ["id", "name", "email", "team", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]