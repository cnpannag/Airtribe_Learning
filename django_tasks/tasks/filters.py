import django_filters
from django.db import models

from .models import Task


class TaskFilter(django_filters.FilterSet):
    """
    Filter on any Task field via query params (values come from the URL).

    Text fields use icontains so ?title=Postgres -> WHERE title ILIKE '%Postgres%'
    Other fields use their type's default (exact for bool, id, FK, datetimes).

    Note: fields="__all__" skips the primary key, so id is listed explicitly.

    Examples:
      /api/tasks/?title=Postgres
      /api/tasks/?description=linked
      /api/tasks/?completed=true
      /api/tasks/?user=1
      /api/tasks/?id=3
      /api/tasks/?completed=false&title=API&page=1
    """

    class Meta:
        model = Task
        # Explicit list = every Task column, including id (__all__ omits the PK)
        fields = [
            "id",
            "title",
            "description",
            "completed",
            "created_at",
            "updated_at",
            "user",
        ]
        filter_overrides = {
            models.CharField: {
                "filter_class": django_filters.CharFilter,
                "extra": lambda f: {"lookup_expr": "icontains"},
            },
            models.TextField: {
                "filter_class": django_filters.CharFilter,
                "extra": lambda f: {"lookup_expr": "icontains"},
            },
        }
