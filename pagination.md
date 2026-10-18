user --> API --> DB
user makes a req to api, api asks the db and db will return the data to api and api to user

data in DB is stored in ROM but when travelling to api will be via a network.
in the API server --> this data coming from DB will be stored in RAM. 
say 1tb data coming from DB --> API is storing this data 

Problem 1:
with multiple users querying data via api server --> RAM on API server will get choked

Problem 2:
Similar limitation of network bandwidth apply

Problem 3:
Because of all this the time take for user to get data from db will be high

Problem 4:
Laptop limitations will also apply here, how will 1tb of data be shown simultaniously be loaded into the browser

Solution: 
Break into chuncks -> 1 kb * 1000 --> this is called *Pagination*


ex: Amazon will show 45 shoes per page and will load over 900 pages of shoes

here Amazon will only have to extract the first 45 shoe details until the user goes to the second page
This is where *Pagination* will be used in real life

in DB how do we write query for this? 
select * from tasks_task limit 45 *offset 0*;  --> Page 1
select * from tasks_task limit 45 *offset 45*;  --> Page 2
*offset* is the number of items to skip before select and limit apply

doing this in Django:
settings.py :
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
}

## What we changed to turn pagination on

Only `config/settings.py` actually enables pagination. `ModelViewSet.list` already calls `paginate_queryset`. Once `DEFAULT_PAGINATION_CLASS` is set, `GET /api/tasks/` returns pages by itself. No pagination code was added to the view.

The live server is `http://127.0.0.1:8002`. Port `8001` was not running.

### API call and result (Approach 1 — global page size 10)

With only the settings default (before `TaskPagination`), `GET http://127.0.0.1:8002/api/tasks/?page=1` returns 10 rows per page.

With the live setup (Approach 2 on tasks), use `page_size` as below.

DRF turns `?page=1` into `LIMIT 10 OFFSET 0`, and `?page=2` into `LIMIT 10 OFFSET 10`.

### `django_tasks/config/settings.py`

Added:

```python
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
}
```

`DEFAULT_PAGINATION_CLASS` must stay a string. Do not write `from rest_framework.pagination import PageNumberPagination` in this file.

That import runs while Django is still loading settings, before `REST_FRAMEWORK` exists. `PageNumberPagination` reads `PAGE_SIZE` at import time and caches it. The cache was `None`, so `/api/tasks/` kept returning every row (about 200 KB, 1003 tasks) even though `PAGE_SIZE` was 10. Removing the import fixed it. The dev server had to reload after that change.

### `django_tasks/tasks/views.py`

No pagination class was added here. `TaskViewSet(ModelViewSet)` uses the global setting for `list` (`GET /api/tasks/`).

Custom actions do not. `get_incomplete_tasks` and `get_user_tasks` build `Response(serializer.data)` themselves, so they still return the full queryset.

The older function views (`add_numbers` and its imports) were commented out in the same pass. That cleanup is separate from pagination.

### `django_tasks/tasks/urls.py`

No new route. The router was already `router.register(r'tasks', TaskViewSet)`.

Commented out `from rest_framework.pagination import PageNumberPagination`. That import did not configure pagination, and it was unused. Also commented out `path("add-numbers/", add_numbers)`.

## Approach 2: custom `TaskPagination` on the viewset

Approach 1 (global `REST_FRAMEWORK` in settings) always returns 10 rows and ignores `?page_size=`. Approach 2 subclasses `PageNumberPagination` so this viewset can pick its own default size, accept `page_size` from the query string, and cap how large that size can get.

### `django_tasks/tasks/pagination.py`

```python
from rest_framework.pagination import PageNumberPagination

class TaskPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 50
```

| Attribute | Meaning |
| --- | --- |
| `page_size` | Default rows per page when the client omits `page_size` (20, not the global 10). |
| `page_size_query_param` | Query key the client may send, e.g. `?page_size=30`. |
| `max_page_size` | Hard cap. `?page_size=500` becomes 50. |

The file must be `.py`. An earlier `pagination.oy` was never imported by Django.

### `django_tasks/tasks/views.py`

```python
from .pagination import TaskPagination

class TaskViewSet(ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    pagination_class = TaskPagination
```

`pagination_class` on the viewset overrides the global default for `TaskViewSet` only. `UserViewSet` still uses the settings default of 10.

### How to call it

| URL | Rows returned |
| --- | --- |
| `/api/tasks/?page=1` | 20 (default from `TaskPagination.page_size`) |
| `/api/tasks/?page=1&page_size=20` | 20 |
| `/api/tasks/?page=1&page_size=30` | 30 |
| `/api/tasks/?page=1&page_size=500` | 50 (capped by `max_page_size`) |

### API call and result

`GET http://127.0.0.1:8002/api/tasks/?page=1&page_size=2`

```json
{
  "count": 1003,
  "next": "http://127.0.0.1:8002/api/tasks/?page=2&page_size=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "Learn Postgres",
      "description": "first row",
      "completed": false,
      "user": null
    },
    {
      "id": 2,
      "title": "models.CharField(max_length=200)",
      "description": "models.TextField(blank=True)",
      "completed": true,
      "user": null
    }
  ]
}
```

`count` is the full table size. `next` keeps `page_size`. Page 2 would be `...?page=2&page_size=2`.

Approach 1 stays in `settings.py` as the project-wide fallback. Approach 2 only changes tasks. Both still use `LIMIT` / `OFFSET` under the hood.

## Approach 3 (later): cursor pagination

Large offsets get slow. `?page=500` is `OFFSET 4990`. Postgres still walks the skipped rows. Inserts and deletes also shift which rows land on a page.

`CursorPagination` pages by a stable column such as `id` or `created_at` (`WHERE id > last_seen_id LIMIT 10`) instead of skipping rows with `OFFSET`. Page numbers go away. The client follows `next`. That stays fast and does not shuffle rows when someone inserts a task.

## Filtering + pagination together

Filtering picks rows (`WHERE`). Pagination then slices that result (`LIMIT` / `OFFSET`).

```
/api/tasks/?completed=true&title=Postgres&page=1&page_size=20
```

→ `WHERE completed = true AND title ILIKE '%Postgres%' LIMIT 20 OFFSET 0`

See `filtering.md`:
- Approach 1: `get_queryset` on `TaskViewSet`
- Approach 2: `filters` dict + `filter(**filters)`
- Approach 3: `django-filter` `TaskFilter` + `DjangoFilterBackend` on `TaskViewSet`

Search (one `?search=` across fields): DRF `SearchFilter` + `search_fields` — see `search.md`.

Filter ≠ search: search is free text across columns; filter is exact/structured per field (`completed`, `user`, `id`). You usually need both — see `filtering.md` / `search.md`.

Ordering (`?ordering=-id`): DRF `OrderingFilter` + `ordering_fields` — see `ordering.md`.

Combined example:

`GET /api/tasks/?completed=false&search=API&ordering=-id&page=1&page_size=2`