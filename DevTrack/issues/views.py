from django.shortcuts import render
# Create your views here.

from .models import Issue, IssueSchema, ReporterSchema, LowPriorityIssue, CriticalIssue
from .serializer import IssueSerializer, ReporterSerializer
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response



class IssueView(ModelViewSet):
    queryset = IssueSchema.objects.all()
    serializer_class = IssueSerializer
    
    @action(detail=True, methods=["get"], url_path="describe")
    def describe(self, request, pk=None):
        row = self.get_object()
        cls = {"low": LowPriorityIssue, "critical": CriticalIssue}.get(row.priority, Issue)
        issue = cls(row.id, row.title, row.description, row.status, row.priority, row.reporter_id)
        return Response({"summary": issue.describe()})

class ReporterView(ModelViewSet):
    queryset = ReporterSchema.objects.all()
    serializer_class = ReporterSerializer
    
    # @action(detail=False, methods=["get"],url_path="reporters")
    # def get(self, request):
    #     reporters=Issue.objects.values_list("reporter_id", flat=True).distinct()
    #     return Response(reporters)
    
    # @action(detail=False, methods=["post"],url_path="create-issue")
    # def post(self, request):
    #     data=request.data
    #     issue=IssueSerializer(data=data)
    #     issue.save()
    #     return Response(issue.data)
