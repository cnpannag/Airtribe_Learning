from django.shortcuts import render
# Create your views here.

from .models import IssueSchema, ReporterSchema
from .serializer import IssueSerializer, ReporterSerializer
from rest_framework.viewsets import ModelViewSet



class IssueView(ModelViewSet):
    queryset = IssueSchema.objects.all()
    serializer_class = IssueSerializer

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
