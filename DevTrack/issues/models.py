from abc import ABC, ABCMeta, abstractmethod
from django.db import models
from django.db.models.base import ModelBase

class ReporterSchema(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    team = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.name
        
class IssueSchema(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=200)
    priority = models.CharField(max_length=200)
    reporter = models.ForeignKey(ReporterSchema, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
# # We will now get the table as issues_issue  (app name + _ + model name).
# # We can also add a custom name to the table using 
# class Meta:
#     db_table = "issues"  # optional; omit this and Django names it issues_issue
    def __str__(self):
        return self.title
        # return self.title is because we want to return the title of the issue when we print the issue


class BaseEntity(ABC):
    @abstractmethod
    def validate(self):
        pass

    def to_dict(self):
        return {
            key: value
            for key, value in self.__dict__.items()
        }

class Reporter(BaseEntity):
    def __init__(self, id, name, email, team):
        self.id = id
        self.name = name
        self.email = email
        self.team = team

    def validate(self):
        if not self.name:
            raise ValueError('Name cannot be empty')
        if '@' not in self.email:
            raise ValueError('Invalid email')

class Issue(BaseEntity):
    def __init__(self, id, title, description, status, priority, reporter_id):
        self.id = id
        self.title = title
        self.description = description
        self.status = status
        self.priority = priority
        self.reporter_id = reporter_id

    ALLOWED_STATUSES = {"open", "in_progress", "resolved", "closed"}
    ALLOWED_PRIORITIES = {"low", "medium", "high", "critical"}

    def validate(self):
        if not self.title:
            raise ValueError('Title cannot be empty')
        if self.status not in self.ALLOWED_STATUSES:
            raise ValueError(f"Invalid status: {self.status}")
        if self.priority not in self.ALLOWED_PRIORITIES:
            raise ValueError(f"Invalid priority: {self.priority}")
    
    def describe(self):
        if self.priority == "low":
            return LowPriorityIssue(self.title, self.description, self.status, self.priority, self.reporter_id)
        elif self.priority == "critical":
            return CriticalIssue(self.title, self.description, self.status, self.priority, self.reporter_id)
        else:
            return f"{self.title} [{self.priority}]"

class CriticalIssue(Issue):
    def describe(self):
        return f"[URGENT] {self.title} — needs immediate attention"

class LowPriorityIssue(Issue):
    def describe(self):
        return f"{self.title} — low priority, handle when free"

