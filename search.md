# Search

Filtering asks for **specific fields** (`?completed=true&title=Postgres`).  
Search asks for **one word across several fields** (`?search=Postgres`).

```
GET /api/tasks/?search=Postgres&page=1
```

SQL idea (OR across the listed fields):

```sql
SELECT * FROM tasks_task
WHERE title ILIKE '%Postgres%'
   OR description ILIKE '%Postgres%'
LIMIT 20 OFFSET 0;
```

The search term is **not hard-coded**. Whatever you put after `search=` is the word.

## Easiest approach: DRF `SearchFilter`

Built into Django REST Framework. No extra package. Add it next to your existing `DjangoFilterBackend`.

### `django_tasks/tasks/views.py`

```python
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

class TaskViewSet(ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    pagination_class = TaskPagination
    # Keep django-filter; add SearchFilter (and OrderingFilter)
    # filter_backends = [DjangoFilterBackend]  # older: filters only
    # filter_backends = [DjangoFilterBackend, SearchFilter]  # + search
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = TaskFilter
    search_fields = ["title", "description"]
```

| Piece | Meaning |
| --- | --- |
| `SearchFilter` | Reads `?search=` from the URL. |
| `search_fields` | Which columns get `ILIKE '%word%'`. Match if **any** field hits (OR). |
| `filter_backends` list | Filters, search, and ordering can all run. |

### How to call it

| URL | Meaning |
| --- | --- |
| `/api/tasks/?search=Postgres` | Title or description contains "Postgres" |
| `/api/tasks/?search=API` | Title or description contains "API" |
| `/api/tasks/?completed=false&search=API` | Incomplete **and** search match |
| `/api/tasks/?search=Postgres&page=1&page_size=20` | Search, then paginate |

### API calls and results

**Search Postgres**

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

**Search API**

`GET http://127.0.0.1:8002/api/tasks/?search=API&page=1&page_size=2`

```json
{
  "count": 100,
  "next": "http://127.0.0.1:8002/api/tasks/?page=2&page_size=2&search=API",
  "previous": null,
  "results": [
    {"id": 4, "title": "Write API tests #1", "completed": false, "user": 1},
    {"id": 14, "title": "Write API tests #11", "completed": false, "user": 1}
  ]
}
```

**Filter + search**

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

### Why filtering if I already have search?

They answer different questions. Search is a **text box**. Filtering is a **set of precise controls**.

| Need | Use | Why search alone is not enough |
| --- | --- | --- |
| "Find anything about Postgres" | `?search=Postgres` | Search is built for this — one word, many text fields. |
| "Only incomplete tasks" | `?completed=false` | `completed` is a boolean. Searching `"false"` in title/description does not mean "status = false". |
| "Only tasks for user 1" | `?user=1` | `user` is an id (FK). Search does not look at `user` unless you add it to `search_fields`, and even then `"1"` matching inside a title is wrong. |
| "Title contains API **and** completed is true" | `?title=API&completed=true` | Search ORs fields. Filters AND exact conditions. |
| "I typed a word; I don't care which column" | `?search=API` | Filter would force you to pick `title=` or `description=` separately. |

**Search** (`SearchFilter`):

- One param: `?search=word`
- Runs `ILIKE '%word%'` on each of `search_fields`
- Combines those field checks with **OR**
- Best for free-text: titles, descriptions, names

**Filter** (`DjangoFilterBackend` / `TaskFilter`):

- One param **per field**: `?completed=`, `?user=`, `?id=`, `?title=`
- Exact or typed lookups (bool, FK, id, contains on one chosen field)
- Combines params with **AND**
- Best for structured facets: status, owner, id, dates

Real product UI:

- Search box → `?search=...`
- Checkboxes / dropdowns ("Completed?", "Assigned to?") → `?completed=` / `?user=`

You usually want **both on the same request**:

`GET /api/tasks/?completed=false&search=API&page=1`

→ incomplete **and** (title or description contains API). That is filter + search together. Search alone cannot express the boolean status cleanly.

| | Filter (`?title=` / `?completed=`) | Search (`?search=`) |
| --- | --- | --- |
| Params | One param per field | One param for many fields |
| Logic | AND across params | OR across `search_fields` |
| Field types | Bool, FK, id, dates, text | Mostly text |
| Setup | `TaskFilter` + `DjangoFilterBackend` | `search_fields` + `SearchFilter` |

Add `?ordering=-id` to sort (see `ordering.md`). Pagination still applies after them.
