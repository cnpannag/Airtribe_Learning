# Filtering

Pagination answers **how many rows** to return. Filtering answers **which rows** — with **precise, per-field** conditions.

```
user --> API --> DB
GET /api/tasks/?completed=true&title=Postgres&page=1
```

The API builds a `WHERE` clause, then applies `LIMIT` / `OFFSET` for the page.

## Why filtering if I already have search?

Search (`?search=Postgres`) is one free-text box across several text columns (OR + `ILIKE '%…%'`). Filtering is for **structured** questions search cannot answer cleanly:

| You want | Filter | Why not only `?search=` |
| --- | --- | --- |
| Incomplete tasks | `?completed=false` | Status is a boolean column, not a word in the title. |
| Tasks owned by user 1 | `?user=1` | Exact FK / id match. Searching `"1"` would wrongly hit titles that contain "1". |
| Title contains X **and** completed | `?title=X&completed=true` | Filters AND conditions. Search ORs text fields only. |
| Exact row by primary key | `?id=3` | Id equality, not text search. |

Search is still better when the user types a word and you do not care whether it sits in `title` or `description`:

`?search=API` → title **or** description contains API.

Typical API / UI pairing:

- Search box → `?search=`
- Filters (status, assignee, …) → `?completed=` / `?user=`
- Together → `?completed=false&search=API&page=1`

See also the longer comparison in `search.md`.

## SQL you already know

The search word is **not hard-coded**. Whatever you put after `title=` in the URL is the search term. `Postgres` below is only an example of a value you type.

```sql
-- completed = true
SELECT * FROM tasks_task WHERE completed = true;

-- title like '%<word from URL>%'  (case-insensitive in Django: ILIKE)
-- e.g. ?title=Postgres  ->  ILIKE '%Postgres%'
-- e.g. ?title=API       ->  ILIKE '%API%'
SELECT * FROM tasks_task WHERE title ILIKE '%Postgres%';

-- both, then page 1 of 20
SELECT * FROM tasks_task
WHERE completed = true AND title ILIKE '%Postgres%'
LIMIT 20 OFFSET 0;
```

## Django ORM lookups

| Query param intent | ORM | SQL |
| --- | --- | --- |
| `completed=true` | `filter(completed=True)` | `WHERE completed = true` |
| `title=<any word>` | `filter(title__icontains=<that word>)` | `WHERE title ILIKE '%<that word>%'` |

`title = self.request.query_params.get("title")` reads the word from the URL. `__icontains` wraps it with `%` on both sides. Other common lookups: `__exact`, `__startswith`, `__gt`, `__lte`.

## Approach 1: `get_queryset` on the viewset

`ModelViewSet.list` always calls `get_queryset()` before pagination. Override it, read query params, chain `.filter()`.

**`django_tasks/tasks/views.py`** (on `TaskViewSet`):

```python
def get_queryset(self):
    queryset = Task.objects.all()

    completed = self.request.query_params.get("completed")
    if completed is not None:
        is_completed = completed.lower() in ("true", "1", "yes")
        queryset = queryset.filter(completed=is_completed)

    title = self.request.query_params.get("title")
    if title:
        queryset = queryset.filter(title__icontains=title)

    return queryset
```

Omit a param → that filter is skipped. Both params → `AND` in SQL.

### How to call it

| URL | Meaning |
| --- | --- |
| `/api/tasks/?completed=true` | Only completed tasks |
| `/api/tasks/?completed=false` | Only incomplete tasks |
| `/api/tasks/?title=Postgres` | Title contains "Postgres" |
| `/api/tasks/?completed=true&title=Postgres` | Both conditions |
| `/api/tasks/?completed=true&title=Postgres&page=1&page_size=20` | Filter, then paginate |

Example:

`http://127.0.0.1:8002/api/tasks/?completed=true&title=Postgres&page=1&page_size=20`

`count` in the response is the **filtered** total, not the full table. `next` keeps the same filter params.

### Relation to `get_incomplete_tasks`

That custom action hard-codes `filter(completed=False)` on its own URL. `?completed=false` on the list endpoint does the same filter, and also gets pagination. Filtering on `get_queryset` is the reusable pattern; the custom action is an earlier, fixed shortcut.

## Approach 2: build a `filters` dict, then `filter(**filters)`

Same idea as Approach 1 (only apply a filter when the query param is present), but collect lookups in a dictionary and unpack them once.

```python
def get_tasks_with_filter(request):
    """
    To achieve this, we modify the database query to include the filters.
    If any filter is passed, it is added to the DB query.
    If no filter is passed, all tasks are returned.
    """
    # completed and title are applied only when they are passed.
    # If a param is missing, that filter is skipped.
    filters = {}

    if "completed" in request.query_params:
        filters["completed"] = request.query_params["completed"].lower() == "true"

    if request.query_params.get("title"):
        # word still comes from the URL — not hard-coded
        filters["title__endswith"] = request.query_params["title"]

    tasks = Task.objects.filter(**filters)  # all tasks if filters = {}
    serializer = TaskSerializer(tasks, many=True)
    return Response(serializer.data)
```

| Piece | Meaning |
| --- | --- |
| `filters = {}` | Start with no `WHERE` clauses. |
| `filters["completed"] = ...` | Add exact match on `completed` when `?completed=` is present. |
| `filters["title__endswith"] = ...` | Add `WHERE title LIKE '%word'` (ends with the URL word). |
| `filter(**filters)` | Unpack the dict into kwargs. `{}` → same as no filters (all rows). |

`**filters` turns `{"completed": True, "title__endswith": "Postgres"}` into:

```python
Task.objects.filter(completed=True, title__endswith="Postgres")
```

### Approach 1 vs Approach 2

| | Approach 1 (`get_queryset`) | Approach 2 (`filters` dict) |
| --- | --- | --- |
| Where it lives | Method on `TaskViewSet` | Standalone function view (or same logic inside `get_queryset`) |
| How filters are applied | Chain `.filter(...)` calls | Build a dict, one `.filter(**filters)` |
| Title lookup in our notes | `title__icontains` → `ILIKE '%word%'` | `title__endswith` → `LIKE '%word'` (suffix only) |
| Pagination | Yes (list uses `TaskPagination`) | Not automatic; this example returns the full filtered list |

Both still take the search word from `?title=` in the URL. To get "contains anywhere" with Approach 2, use `title__icontains` as the dict key instead of `title__endswith`.

## Approach 3: `django-filter`

Declare a `FilterSet`. DRF applies it on the list endpoint — no manual `if` blocks on the viewset. This is the approach currently wired in the project code.

To filter on **any** model field, set `fields = "__all__"`. Use `filter_overrides` so text fields still behave like Approach 1 (`icontains` / `ILIKE '%…%'`).

### Install and settings

```text
pip install django-filter
```

**`requirements.txt`**: `django-filter==26.2`

**`config/settings.py`**: add `"django_filters"` to `INSTALLED_APPS`.

### `django_tasks/tasks/filters.py`

```python
import django_filters
from django.db import models
from .models import Task

class TaskFilter(django_filters.FilterSet):
    class Meta:
        model = Task
        # List every column. fields="__all__" would skip the primary key (id).
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
            # ?title=Postgres / ?description=linked  ->  ILIKE '%…%'
            models.CharField: {
                "filter_class": django_filters.CharFilter,
                "extra": lambda f: {"lookup_expr": "icontains"},
            },
            models.TextField: {
                "filter_class": django_filters.CharFilter,
                "extra": lambda f: {"lookup_expr": "icontains"},
            },
        }
```

| Meta option | Meaning |
| --- | --- |
| `fields = [...]` | Auto-generate a filter for each listed column (`id`, `title`, `description`, `completed`, `created_at`, `updated_at`, `user`). |
| Why not `"__all__"`? | django-filter's `"__all__"` omits the primary key, so `?id=3` would be ignored. |
| `filter_overrides` | For `CharField` / `TextField`, use `icontains` so `?title=` still means "contains", not exact match. |
| Other field types | Keep the default (exact): `?completed=true`, `?user=1`, `?id=3`. |

Values still come from the URL. When you add a new field on `Task`, add its name to this `fields` list.

### `django_tasks/tasks/views.py`

```python
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from .filters import TaskFilter

class TaskViewSet(ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    pagination_class = TaskPagination
    # filter_backends = [DjangoFilterBackend]  # filters only
    # filter_backends = [DjangoFilterBackend, SearchFilter]  # + search
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = TaskFilter
    search_fields = ["title", "description"]
    ordering_fields = ["id", "title", "completed", "created_at", "updated_at"]
    ordering = ["id"]
```

`filter_backends` tells DRF to run django-filter (and search). `filterset_class` points at `TaskFilter`.

### How to call it

| URL | Meaning |
| --- | --- |
| `/api/tasks/?completed=true` | `WHERE completed = true` |
| `/api/tasks/?title=Postgres` | `WHERE title ILIKE '%Postgres%'` |
| `/api/tasks/?description=linked` | `WHERE description ILIKE '%linked%'` |
| `/api/tasks/?user=1` | `WHERE user_id = 1` |
| `/api/tasks/?id=3` | `WHERE id = 3` |
| `/api/tasks/?completed=false&title=API&page=1&page_size=20` | Combine any fields, then paginate |

### API calls and results

**Title contains Postgres**

`GET http://127.0.0.1:8002/api/tasks/?title=Postgres&page=1&page_size=2`

```json
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "Learn Postgres",
      "description": "first row",
      "completed": false,
      "user": null
    }
  ]
}
```

**Incomplete tasks**

`GET http://127.0.0.1:8002/api/tasks/?completed=false&page=1&page_size=2`

```json
{
  "count": 669,
  "next": "http://127.0.0.1:8002/api/tasks/?completed=false&page=2&page_size=2",
  "previous": null,
  "results": [
    {"id": 1, "title": "Learn Postgres", "completed": false, "user": null},
    {"id": 3, "title": "Task for user 1", "completed": false, "user": 1}
  ]
}
```

**Tasks for user 1**

`GET http://127.0.0.1:8002/api/tasks/?user=1&page=1&page_size=2`

```json
{
  "count": 801,
  "next": "http://127.0.0.1:8002/api/tasks/?page=2&page_size=2&user=1",
  "previous": null,
  "results": [
    {"id": 3, "title": "Task for user 1", "completed": false, "user": 1},
    {"id": 4, "title": "Write API tests #1", "completed": false, "user": 1}
  ]
}
```

`count` is the **filtered** total. `next` keeps the same filter params. Pagination still comes from `TaskPagination`.

Note: `?completed=true&title=Postgres` can return `count: 0` if that task is incomplete (id 1 is `completed: false`).

## Search (easiest): DRF `SearchFilter`

One query param (`?search=`) across several fields with OR + `icontains`. Built into DRF — no new package. Lives next to Approach 3 filters; nothing was removed.

See `search.md` for the full write-up. Short version on the viewset:

```python
from rest_framework.filters import SearchFilter, OrderingFilter

# filter_backends = [DjangoFilterBackend, SearchFilter]
filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
search_fields = ["title", "description"]
```

| URL | Meaning |
| --- | --- |
| `/api/tasks/?search=Postgres` | Title **or** description contains "Postgres" |
| `/api/tasks/?completed=false&search=API&page=1` | Filter + search + page |

### API call and result

`GET http://127.0.0.1:8002/api/tasks/?search=Postgres&page=1&page_size=2`

```json
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {"id": 1, "title": "Learn Postgres", "completed": false, "user": null}
  ]
}
```

`GET http://127.0.0.1:8002/api/tasks/?completed=false&search=API&page=1&page_size=2`

```json
{
  "count": 67,
  "next": "http://127.0.0.1:8002/api/tasks/?completed=false&page=2&page_size=2&search=API",
  "previous": null,
  "results": [
    {"id": 4, "title": "Write API tests #1", "completed": false, "user": 1},
    {"id": 14, "title": "Write API tests #11", "completed": false, "user": 1}
  ]
}
```

## Ordering (easiest): DRF `OrderingFilter`

`?ordering=-id` sorts descending by id. See `ordering.md`.

```python
ordering_fields = ["id", "title", "completed", "created_at", "updated_at"]
ordering = ["id"]
```

`GET http://127.0.0.1:8002/api/tasks/?ordering=-id&page=1&page_size=2` → ids `1003`, `1002` first.
