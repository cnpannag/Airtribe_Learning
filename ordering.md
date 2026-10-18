# Ordering

Pagination answers **how many** rows. Filtering / search answer **which** rows. Ordering answers **in what order**.

```
GET /api/tasks/?ordering=-id&page=1&page_size=2
```

SQL idea:

```sql
SELECT * FROM tasks_task
ORDER BY id DESC
LIMIT 2 OFFSET 0;
```

`-id` means descending. `id` (no minus) means ascending. The field name comes from the URL — not hard-coded beyond the allow-list in `ordering_fields`.

## Easiest approach: DRF `OrderingFilter`

Built into Django REST Framework. No extra package. Add it next to `DjangoFilterBackend` and `SearchFilter`.

### `django_tasks/tasks/views.py`

```python
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

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
    ordering = ["id"]  # default when ?ordering= is omitted
```

| Piece | Meaning |
| --- | --- |
| `OrderingFilter` | Reads `?ordering=` from the URL. |
| `ordering_fields` | Allow-list. Client can only sort by these columns (safety). |
| `ordering` | Default sort when the client omits `?ordering=`. |
| Leading `-` | Descending: `?ordering=-created_at`. |

### API calls and results

**Newest id first**

`GET http://127.0.0.1:8002/api/tasks/?ordering=-id&page=1&page_size=2`

```json
{
  "count": 1003,
  "next": "http://127.0.0.1:8002/api/tasks/?ordering=-id&page=2&page_size=2",
  "previous": null,
  "results": [
    {"id": 1003, "title": "Review pull request #1000", "completed": false},
    {"id": 1002, "title": "Verify login flow #999", "completed": true}
  ]
}
```

**Title A→Z**

`GET http://127.0.0.1:8002/api/tasks/?ordering=title&page=1&page_size=2`

```json
{
  "count": 1003,
  "next": "http://127.0.0.1:8002/api/tasks/?ordering=title&page=2&page_size=2",
  "previous": null,
  "results": [
    {"id": 108, "title": "Add user filter #105", "completed": true},
    {"id": 118, "title": "Add user filter #115", "completed": false}
  ]
}
```

**Search + ordering (API matches, newest first)**

`GET http://127.0.0.1:8002/api/tasks/?search=API&ordering=-id&page=1&page_size=2`

```json
{
  "count": 100,
  "next": "http://127.0.0.1:8002/api/tasks/?ordering=-id&page=2&page_size=2&search=API",
  "previous": null,
  "results": [
    {"id": 994, "title": "Write API tests #991", "completed": false},
    {"id": 984, "title": "Write API tests #981", "completed": true}
  ]
}
```

**Filter + search + ordering + page**

`GET http://127.0.0.1:8002/api/tasks/?completed=false&search=API&ordering=-id&page=1&page_size=2`

```json
{
  "count": 67,
  "next": "http://127.0.0.1:8002/api/tasks/?completed=false&ordering=-id&page=2&page_size=2&search=API",
  "previous": null,
  "results": [
    {"id": 994, "title": "Write API tests #991", "completed": false},
    {"id": 974, "title": "Write API tests #971", "completed": false}
  ]
}
```

### Ordering vs filter vs search

| | Filter | Search | Ordering |
| --- | --- | --- | --- |
| Param | `?title=` / `?completed=` | `?search=` | `?ordering=` |
| Changes | Which rows | Which rows (OR across fields) | Sort of those rows |
| Setup | `TaskFilter` | `search_fields` | `ordering_fields` |

All three can appear on one URL. Pagination runs last.
