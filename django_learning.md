create a venv,
activate a venv 
venv.md has commands

create a django_tasks folder and cd to it
pip install django
pip install djangorestframework 

django-admin startproject config .
python manage.py migrate
python manage.py runserver 8081

clearing port if required:
netstat -ano | findstr :8000
run powershell in admin mode >>  taskkill /PID 912 /F

Go To > http://127.0.0.1:8081 > Django!
ctrl c

"python manage.py startapp tasks" command > will create app files like init.py, app.py, etc 
all the code we write will be in these files 
1 task is 1 app


settings.py is the most imp file > it controls access throughtout the app
urls.py > controls the urls blueprint we want to have in our app
config folder is for the entire project
task folder is for 1 app

REST API
About 10 years ago
    User >> Application(FE+BE) 
    >> BE would control the FE

Today:
   REST API: User --> FE <---> BE  
   >> FE is separate and is not controled by BE. both work in parallel by talking to each other

REST API is backend apis that take a request and return a respond. they mostly work with JSON

---

# Postgres, Docker, model, serializer, and ModelViewSet

The JSON file APIs (`tasks/files/tasks.json`) are still there. The new path stores tasks in Postgres. Django never talks to Postgres by writing SQL in the view. The chain is:

`HTTP request` → `URL` → `ModelViewSet` → `TaskSerializer` → `Task` model → Postgres table `tasks_task`

## What each file is for

| File | Job |
| --- | --- |
| `docker-compose.yml` | Starts a Postgres container on your machine |
| `django_tasks/config/settings.py` | Tells Django which database to use |
| `django_tasks/config/urls.py` | Sends anything under `/api/` into the tasks app |
| `django_tasks/tasks/models.py` | Python description of the table |
| `django_tasks/tasks/serializer.py` | Converts a row to JSON, and JSON from a request into a row |
| `django_tasks/tasks/views.py` | `TaskViewSet` handles list, get-one, create, update, partial update, delete |
| `django_tasks/tasks/urls.py` | Registers that viewset at `/api/tasks/` |
| `django_tasks/tasks/migrations/` | The history of table changes Django has applied |

The serializer file is named `serializer.py` (singular). The import in views is `from .serializer import TaskSerializer`.

## Model

`tasks/models.py`:

```python
class Task(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

Django turns this class into the table `tasks_task`. The name is always `appname_modelname` in lowercase: app `tasks` + model `Task` = `tasks_task`.

| Model field | Postgres column | Meaning |
| --- | --- | --- |
| (automatic) | `id` | Primary key. Postgres creates it. The client does not send it. |
| `title` | `title` | Required text, max 200 characters |
| `description` | `description` | Optional longer text. `blank=True` means the API may omit it. |
| `completed` | `completed` | Boolean. Default `false`. Stored as `t` / `f` in psql. |
| `created_at` | `created_at` | Set once, when the row is inserted. `auto_now_add=True`. |
| `updated_at` | `updated_at` | Set on insert and refreshed on every save. `auto_now=True`. |

`created_at` and `updated_at` were added after the first row already existed. Postgres needs a value for old rows, so that row was filled with the time of the migration (`2026-10-10 06:41:53+00`). New rows get the real insert time.

A model change does nothing to Postgres until you migrate:

```powershell
cd django_tasks
python manage.py makemigrations tasks
python manage.py migrate
```

- `makemigrations` writes a file such as `tasks/migrations/0002_task_created_at_task_updated_at.py`. This is the plan.
- `migrate` runs that plan against the database. It also records what ran in the table `django_migrations`.
- Adding `auto_now_add=True` onto a table that already has rows asks for a one-off default. That default is only for the old rows. It is not kept as a permanent default.

## Serializer

`tasks/serializer.py`:

```python
class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ["id", "title", "description", "completed", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]
```

You do not run this file. A view calls it.

Two directions:

- **Out (database → JSON):** `TaskSerializer(task).data` or `TaskSerializer(tasks, many=True).data`. `many=True` is required when the value is a list or queryset, as in `GET /api/tasks/`.
- **In (JSON → database):** `TaskSerializer(data=request.data)`. `is_valid()` checks the JSON against the model. `save()` runs the INSERT. For an update, pass the existing row as well: `TaskSerializer(task, data=request.data)`.

`read_only_fields` means the client cannot set `id`, `created_at`, or `updated_at`. Postgres and Django set those. If a POST body includes them, they are ignored.

A failed check returns `400` and a JSON object of field errors, for example `{"title": ["This field is required."]}`.

## ViewSet and ModelViewSet

A viewset is one class that owns a whole resource, instead of a separate function for each URL.

`ViewSet` is the manual version. The commented class in `views.py` writes each action by hand:

| Method on the class | HTTP | What it does |
| --- | --- | --- |
| `list` | GET collection | `Task.objects.all()` |
| `retrieve` | GET one | `Task.objects.get(id=pk)` |
| `create` | POST | `serializer.save()` inserts |
| `update` | PUT | Replace the row. Every writable field must be sent. |
| `partial_update` | PATCH | Change only the fields that were sent. `partial=True` on the serializer. |
| `destroy` | DELETE | `task.delete()` |

`pk` is the primary key from the URL. In this table that is `id`.

`ModelViewSet` is the short version of that same class. The live code is:

```python
class TaskViewSet(ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
```

`queryset` is the database query used to find rows. `serializer_class` is the serializer used for every action. ModelViewSet already implements list, retrieve, create, update, partial_update, and destroy, so those methods do not need to be written again.

`Task.objects` is the Django ORM:

- `Task.objects.all()` → `SELECT * FROM tasks_task`
- `Task.objects.get(id=pk)` → `SELECT * FROM tasks_task WHERE id = pk`. Raises `Task.DoesNotExist` when the id is missing, which becomes HTTP 404.
- `serializer.save()` on a new object → `INSERT`
- `serializer.save()` on an existing object → `UPDATE`
- `task.delete()` → `DELETE`

## How a URL reaches the viewset

1. `config/urls.py` has `path("api/", include("tasks.urls"))`.
2. `tasks/urls.py` has a `DefaultRouter` and `router.register("tasks", TaskViewSet, basename="task")`.
3. `urlpatterns + router.urls` adds the routes below.

Run the server from the `django_tasks` folder. The terminal has been using port `8001`. `8081` also works if that port is free.

```powershell
cd django_tasks
python manage.py runserver 8001
```

Base URL: `http://127.0.0.1:8001`

### Postgres APIs (ModelViewSet)

| Method | URL | Success code | Body |
| --- | --- | --- | --- |
| GET | `/api/tasks/` | 200 | none. Returns one page: `count`, `next`, `previous`, `results`. Tasks use Approach 2 (default 20, optional `page_size`). |
| POST | `/api/tasks/` | 201 | JSON below. Returns the created row, including `id` and timestamps. |
| GET | `/api/tasks/1/` | 200 | none. Returns one row. 404 if that id does not exist. |
| PUT | `/api/tasks/1/` | 200 | Full object: `title`, `description`, `completed`. |
| PATCH | `/api/tasks/1/` | 200 | Only the fields to change, for example `{"completed": true}`. |
| DELETE | `/api/tasks/1/` | 204 | none. Empty body. The row is gone. |

POST example:

```json
{
  "title": "Learn Postgres",
  "description": "first row",
  "completed": false
}
```

PowerShell:

```powershell
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8001/api/tasks/ -ContentType "application/json" -Body '{"title":"Learn Postgres","description":"first row","completed":false}'

Invoke-RestMethod -Method Get -Uri http://127.0.0.1:8001/api/tasks/

Invoke-RestMethod -Method Patch -Uri http://127.0.0.1:8001/api/tasks/1/ -ContentType "application/json" -Body '{"completed": true}'
```

A GET of one task looks like:

```json
{
  "id": 1,
  "title": "Learn Postgres",
  "description": "first row",
  "completed": false,
  "created_at": "2026-10-10T06:41:53.842736Z",
  "updated_at": "2026-10-10T06:41:53.857774Z"
}
```

Restart `runserver` after changing models, serializer, views, or urls. It does not always reload those cleanly while a request is open.

### JSON-file APIs (unchanged, still `tasks.json`)

These do not use Postgres.

| Method | URL |
| --- | --- |
| GET | `/api/hw/` |
| GET | `/api/add-numbers/?a=1&b=2` |
| GET | `/api/get-tasks/` |
| GET | `/api/get-tasks/1/` |
| POST | `/api/create-task/` |
| POST | `/api/create-task-api/` |
| GET | `/api/get-task-api/1/` |
| DELETE | `/api/delete-task-api/1/` |

## Status codes used here

| Code | When |
| --- | --- |
| 200 | GET, PUT, PATCH succeeded |
| 201 | POST created a row |
| 204 | DELETE succeeded. No response body. |
| 400 | JSON failed serializer checks |
| 404 | No row with that `id` |
| 500 | Python crashed. Read the `runserver` terminal. |

## Docker and Postgres

`docker-compose.yml` is in the project root (`python/`, not inside `django_tasks`).

```yaml
services:
  postgres:
    image: postgres:latest
    ports:
      - "5432:5432"
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: postgres
    volumes:
      - postgres_data:/var/lib/postgresql
```

- Image `postgres:latest` is the database program, running in a container.
- `"5432:5432"` means port 5432 on Windows connects to port 5432 inside the container.
- `POSTGRES_USER`, `POSTGRES_PASSWORD`, and `POSTGRES_DB` are the login Django uses.
- `postgres_data` is a Docker volume. Rows survive `docker compose down`. They are removed only if the volume is deleted.

`settings.py` must match the compose file exactly:

```python
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "postgres",
        "USER": "postgres",
        "PASSWORD": "postgres",
        "HOST": "localhost",
        "PORT": "5432",
    }
}
```

Django needs the Python driver `psycopg`. It is already installed. It is listed in `requirements.txt` as `psycopg[binary]==3.3.6`.

There is also a Windows PostgreSQL 18 service listening on port **5433**. Django is not using that one. The API uses the Docker database on **5432**.

### Commands, from the project root

```powershell
docker compose up -d          # start Postgres in the background
docker compose ps             # container name is python-postgres-1
docker compose logs postgres  # if it fails to start
docker compose stop           # stop the container, keep the data
docker compose down           # remove the container, keep the volume
docker compose down -v        # also delete postgres_data. All rows are gone.
```

`up -d` only starts the database. Django is still started separately with `runserver`.

Order when coming back to the project:

```powershell
cd C:\Users\cnpan\Airtribe_Learning\python
docker compose up -d
cd django_tasks
python manage.py migrate
python manage.py runserver 8001
```

`migrate` on a later day does nothing if every migration is already applied. That is expected.

## SQL you can run yourself

Open a psql prompt inside the container:

```powershell
docker exec -it python-postgres-1 psql -U postgres -d postgres
```

One-off query without staying in psql:

```powershell
docker exec python-postgres-1 psql -U postgres -d postgres -c "SELECT * FROM tasks_task;"
```

Inside psql, `\dt` lists tables. Useful ones:

| Table | What it is |
| --- | --- |
| `tasks_task` | Your tasks |
| `django_migrations` | Which migration files have been applied |
| `auth_user` | Django admin users, empty until you create one |
| `django_session` | Login sessions |

Queries:

```sql
SELECT * FROM tasks_task;

SELECT id, title, completed, created_at, updated_at
FROM tasks_task
ORDER BY id;

SELECT * FROM tasks_task WHERE completed = false;

SELECT * FROM tasks_task WHERE id = 1;

SELECT id, title FROM tasks_task WHERE title ILIKE '%postgres%';

SELECT app, name, applied FROM django_migrations ORDER BY applied;
```

`ILIKE` is a case-insensitive match. `%` means "anything".

Insert and update by hand (the API is the normal way; this is just to see the table):

```sql
INSERT INTO tasks_task (title, description, completed, created_at, updated_at)
VALUES ('From SQL', 'typed in psql', false, NOW(), NOW());

UPDATE tasks_task SET completed = true, updated_at = NOW() WHERE id = 1;

DELETE FROM tasks_task WHERE id = 2;
```

Quit psql with `\q`.

A row created through the API shows up in `SELECT * FROM tasks_task` immediately. A row inserted with SQL shows up in `GET /api/tasks/` immediately. Same table.


Postgres is already connected in settings, and Docker is running with the same user, password, and database. You do not write a `CREATE TABLE` statement. Django creates the table from a model class when you run migrations.

The piece that is still missing is the database model. `Issue` in `DevTrack/issues/models.py` is a normal Python class. `IssueSerializer` and `IssueView` expect a Django model, the same pattern as `Task` in `django_tasks/tasks/models.py`.

## Where the table is defined

Put the columns in `DevTrack/issues/models.py`. The table name is set on the model, not in SQL.

```python
from django.db import models

class Issue(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, default="open")
    priority = models.CharField(max_length=20, default="medium")
    reporter_id = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "issues"  # optional; omit this and Django names it issues_issue
```

- Field names (`title`, `status`, …) become columns.
- `id` is added automatically as the primary key. You do not declare it.
- `db_table = "issues"` forces the Postgres table name. If you leave `Meta` out, Django uses `issues_issue` (`app name` + `_` + `model name`).

Your current `Issue` class (the one with `validate` and `describe`) cannot stay under that same name if the serializer imports it. A `ModelSerializer` and `ModelViewSet` only work with `models.Model`. Keep the domain class under another name, or replace it with this model.

## Commands that create the table

From the `DevTrack` folder, with Docker Postgres still up:

```powershell
cd DevTrack
python manage.py makemigrations issues
python manage.py migrate
```

- `makemigrations` writes a Python migration file under `DevTrack/issues/migrations/`. That file is Django’s version of `CREATE TABLE`.
- `migrate` runs it against the database in `settings.py` (host `localhost`, port `5432`, database `postgres`).

Check the connection before migrating:

```powershell
python manage.py dbshell
```

If that opens a Postgres prompt, the settings are correct.

## What is already done

- `DATABASES` in `DevTrack/config/settings.py` matches `docker-compose.yml` (`postgres` / `postgres` / `postgres` on port `5432`).
- `psycopg` is in `requirements.txt`, which is the Postgres driver Django needs.
- `"issues"` is in `INSTALLED_APPS`.

`HOST` should stay `localhost` while Django runs on your machine and Postgres runs in Docker. Use `postgres` as the host only if Django itself is also a Docker service on the same compose network.

## After the table exists

Wire the API, which is not done yet. `DevTrack/config/urls.py` only has the admin route.

1. Add `DevTrack/issues/urls.py` with a router, same idea as `django_tasks/tasks/urls.py`:

```python
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import IssueView

router = DefaultRouter()
router.register(r"issues", IssueView, basename="issue")

urlpatterns = [
    path("", include(router.urls)),
]
```

2. In `DevTrack/config/urls.py`, add `path("api/", include("issues.urls"))`.

`ModelViewSet` already provides list, retrieve, create, update, and delete. The extra `get` action in `views.py` is not required for that, and `IssueSerializer(issues)` needs `many=True` when serializing a queryset.

I am in Ask mode, so I cannot edit these files. Switch to Agent mode if you want them applied in the project.

---------------------
Great question — you’ve captured the intuition, but let’s break down **@APIView, @ViewSet, and @ModelViewSet** in Django REST Framework (DRF) more precisely. They’re not about performance differences (all run on the same request/response cycle), but about **levels of abstraction and convenience**.

---

## 🔹 `@APIView`
- **What it is**: The most fundamental DRF class-based view. It’s essentially Django’s `View`, but with REST‑friendly request/response handling (parsers, renderers, authentication).
- **Control**: You write each method (`get`, `post`, `put`, `delete`) yourself. Full flexibility.
- **Use case**: When you need **fine-grained control** — custom logic, unusual request/response formats, or non‑CRUD endpoints.
- **Example**:
```python
from rest_framework.views import APIView
from rest_framework.response import Response

class HelloWorld(APIView):
    def get(self, request):
        return Response({"message": "Hello, world!"})
```

---

## 🔹 `@ViewSet`
- **What it is**: A higher abstraction. Instead of writing `get/post/put/delete`, you define **actions** (`list`, `retrieve`, `create`, `update`, `destroy`).
- **Control vs. convenience**: DRF routers can automatically generate URL patterns for these actions. You still write the logic, but you don’t worry about wiring URLs manually.
- **Use case**: When you want **structured CRUD endpoints** but still need to customize logic.
- **Example**:
```python
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response

class HelloViewSet(ViewSet):
    def list(self, request):
        return Response({"message": "Listing items"})
    def retrieve(self, request, pk=None):
        return Response({"message": f"Item {pk}"})
```

---

## 🔹 `@ModelViewSet`
- **What it is**: The most powerful shortcut. It combines a `ViewSet` with a **ModelSerializer** and **QuerySet**.
- **Convenience**: You get full CRUD (`list`, `retrieve`, `create`, `update`, `destroy`) **auto‑implemented**. You only need to declare the model and serializer.
- **Use case**: When you want **rapid development of standard CRUD APIs** with minimal boilerplate.
- **Example**:
```python
from rest_framework.viewsets import ModelViewSet
from .models import Book
from .serializers import BookSerializer

class BookViewSet(ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
```
This gives you a complete REST API for `Book` without writing any methods.

---

## ⚖️ Comparison Summary

| Feature | `APIView` | `ViewSet` | `ModelViewSet` |
|---------|-----------|-----------|----------------|
| **Flexibility** | Maximum | Medium | Minimum |
| **Boilerplate** | High | Medium | Low |
| **CRUD Auto‑gen** | None | Router wiring only | Full CRUD |
| **Best For** | Custom endpoints | Semi‑custom CRUD | Standard CRUD |

---

## 🚀 Key Insight
- **Performance**: All three are equal — they’re just abstractions. The choice is about **developer productivity vs. control**.
- **Rule of Thumb**:
  - Use **APIView** when you need **custom logic** (e.g., ML inference endpoint, complex business rules).
  - Use **ViewSet** when you want **structured CRUD** but with custom behaviors.
  - Use **ModelViewSet** when you want **fast CRUD scaffolding** with minimal code.

---

👉 Since you’re working on **DRF custom actions and routing**, the sweet spot is often **ViewSet**: you get router convenience but can still override methods or add custom actions (`@action(detail=True)` or `@action(detail=False)`).  

Would you like me to show you a **side‑by‑side code example** of adding a custom action in each of the three styles, so you can see how the boilerplate shrinks as you move from `APIView` → `ViewSet` → `ModelViewSet`?

--------------------------

can you pls cover more on Django vs fastapi

**Use FastAPI when you need high‑performance, async APIs for real‑time big data pipelines or ML inference; use Django when you need a full‑stack, ORM‑heavy, admin‑driven platform for managing complex datasets and enterprise workflows.** In practice, many teams combine them: Django for the core product and FastAPI for high‑throughput microservices.  [azguards.com](https://azguards.com/python/fastapi-vs-django-in-2026-which-python-framework-wins/)  [codeoxi.com](https://codeoxi.com/blog/fastapi-vs-django)  [toolchew.com](https://toolchew.com/en/django-vs-fastapi/)  

---

## ⚖️ Django vs FastAPI for Big Data

### Core Differences
| Factor | **FastAPI** | **Django** |
|--------|-------------|-------------|
| **Architecture** | Async‑first (ASGI, Starlette, uvicorn) | Sync core, async views in Django 5.x |
| **Performance** | ~12,000–20,000 RPS, lower latency (95ms P99) | ~8,500 RPS, higher latency (180ms P99) |
| **ORM** | Bring your own (SQLAlchemy, Tortoise) | Mature, built‑in ORM with optimized queries |
| **Admin Panel** | None (third‑party options immature) | Full CRUD admin auto‑generated |
| **Best For** | Real‑time APIs, ML inference, streaming, microservices | Enterprise apps, complex data models, dashboards |
| **Learning Curve** | Gentle for API‑only work | Steeper, more concepts (ORM, templates, forms) |

---

## 📊 Big Data Perspective

- **FastAPI Strengths**
  - **Async I/O**: Handles thousands of concurrent requests efficiently, ideal for **data ingestion pipelines, streaming APIs, and ML model serving**.
  - **Integration with ML ecosystem**: Hugging Face, LangChain, and PySpark often use FastAPI as the serving layer.
  - **Cloud efficiency**: Higher throughput translates to **lower cloud costs** for traffic‑heavy workloads.

- **Django Strengths**
  - **ORM & Admin**: Excellent for **data management, CRUD dashboards, and enterprise reporting**.
  - **Predictable queries**: In low‑concurrency, DB‑heavy workloads, Django’s ORM can outperform FastAPI by ~15% in real‑DB CRUD tests.
  - **Batteries included**: Authentication, forms, migrations, and admin panel save months of development for **data‑driven enterprise platforms**.

---

## 🚨 Trade‑offs & Risks

- **FastAPI Risks**
  - No built‑in admin → extra work for managing big datasets.
  - Async complexity → debugging event‑loop issues can be harder.
  - ORM maturity lower than Django’s; SQLAlchemy/Tortoise require more setup.

- **Django Risks**
  - Higher latency under extreme concurrency → less suited for **real‑time streaming APIs**.
  - Async support still partial; ORM remains synchronous, limiting scalability for **high‑throughput big data ingestion**.
  - Heavier framework → slower startup and more resource usage.

---

## ✅ Recommendation for You (Big Data Context)

- **Choose FastAPI** if your workload is **real‑time, high‑concurrency, or ML‑driven** (e.g., serving PySpark results, streaming Kafka events, ML inference APIs).
- **Choose Django** if your workload is **enterprise data management** (e.g., dashboards, CRUD apps, reporting systems, admin‑driven workflows).
- **Hybrid Approach**: Many organizations run **Django for the core product** (admin, ORM, user management) and **FastAPI for high‑throughput microservices** (ML serving, async APIs). This balances developer velocity with performance.

---

👉 Since you’re already working with **PySpark, caching, and AWS**, I’d suggest **FastAPI for your real‑time data APIs** and **Django for internal dashboards/admin tools**. This way, you get the best of both worlds: **speed for big data pipelines** and **structure for enterprise data management**.  

Would you like me to sketch a **step‑by‑step architecture diagram** showing how Django and FastAPI can co‑exist in a big data stack (with Spark, Redis, and AWS)?
--------------------------------



## Pagination

`GET /api/tasks/` uses page-number pagination. The server is on port **8002**:

`http://127.0.0.1:8002/api/tasks/?page=1&page_size=20`

```json
{
  "count": 1003,
  "next": "http://127.0.0.1:8002/api/tasks/?page=2&page_size=20",
  "previous": null,
  "results": []
}
```

Live sample with `page_size=2`:

`GET http://127.0.0.1:8002/api/tasks/?page=1&page_size=2`

```json
{
  "count": 1003,
  "next": "http://127.0.0.1:8002/api/tasks/?page=2&page_size=2",
  "previous": null,
  "results": [
    {"id": 1, "title": "Learn Postgres", "completed": false, "user": null},
    {"id": 2, "title": "models.CharField(max_length=200)", "completed": true, "user": null}
  ]
}
```

### Approach 1: global setting

**`django_tasks/config/settings.py`** turns pagination on for every list view that does not set its own class:

```python
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
}
```

Keep `DEFAULT_PAGINATION_CLASS` as a string. Do not import `PageNumberPagination` in `settings.py`. That import runs before `REST_FRAMEWORK` is assigned. The pagination class reads `PAGE_SIZE` while it is imported and caches `None`. The list endpoint then returns the whole table.

With only Approach 1, `GET /api/tasks/?page=1` returns 10 tasks. `?page_size=` is ignored. DRF runs `LIMIT 10 OFFSET 0` for page 1.

**`django_tasks/tasks/urls.py`**: the unused `PageNumberPagination` import and the `add-numbers` route were commented out. Neither one configured page size.

Custom actions that return `Response(serializer.data)` still skip pagination. `get_incomplete_tasks` and `get_user_tasks` are unpaginated under both approaches.

### Approach 2: custom `TaskPagination` on the viewset

Lets the tasks list use a different default size, accept `?page_size=`, and cap how large that size can get. Overrides Approach 1 for `TaskViewSet` only.

**`django_tasks/tasks/pagination.py`**:

```python
from rest_framework.pagination import PageNumberPagination

class TaskPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 50
```

**`django_tasks/tasks/views.py`**:

```python
from .pagination import TaskPagination

class TaskViewSet(ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    pagination_class = TaskPagination
```

| URL | Rows |
| --- | --- |
| `/api/tasks/?page=1` | 20 |
| `/api/tasks/?page=1&page_size=20` | 20 |
| `/api/tasks/?page=1&page_size=30` | 30 |
| `/api/tasks/?page=1&page_size=500` | 50 (capped) |

`UserViewSet` still uses Approach 1 (`PAGE_SIZE` 10). Both approaches still use `LIMIT` / `OFFSET`.

### Approach 3 (later): cursor pagination

Switch to `CursorPagination` when the table is large. `OFFSET` still scans every skipped row, and inserts move rows between pages. A cursor pages with `WHERE id > last_id LIMIT 10` and stays stable.

## Filtering

Pagination limits **how many** rows. Filtering chooses **which** rows. Both run on the list endpoint: filter first (`WHERE`), then paginate (`LIMIT` / `OFFSET`).

SQL you want:

```sql
SELECT * FROM tasks_task
WHERE completed = true AND title ILIKE '%Postgres%'
LIMIT 20 OFFSET 0;
```

### Approach 1: `get_queryset` on `TaskViewSet`

Override `get_queryset`. `ModelViewSet.list` calls it before pagination. Read query params and chain ORM filters.

**`django_tasks/tasks/views.py`**:

```python
def get_queryset(self):
    queryset = Task.objects.all()

    completed = self.request.query_params.get("completed")
    if completed is not None:
        is_completed = completed.lower() in ("true", "1", "yes")
        queryset = queryset.filter(completed=is_completed)

    title = self.request.query_params.get("title")
    if title:
        # title__icontains -> ILIKE '%value%'
        queryset = queryset.filter(title__icontains=title)

    return queryset
```

| URL | SQL idea |
| --- | --- |
| `/api/tasks/?completed=true` | `WHERE completed = true` |
| `/api/tasks/?title=Postgres` | `WHERE title ILIKE '%Postgres%'` |
| `/api/tasks/?completed=true&title=Postgres&page=1&page_size=20` | both filters, then page |

Example: `http://127.0.0.1:8002/api/tasks/?completed=true&title=Postgres&page=1&page_size=20`

`count` is the filtered total. `get_incomplete_tasks` is the older fixed shortcut for `completed=False`; `?completed=false` on the list does the same filter and still paginates.

Longer notes: `filtering.md`.

### Approach 2: `filters` dict + `filter(**filters)`

Build a dictionary of lookups only for params that were sent, then unpack once. The search word still comes from the URL.

```python
def get_tasks_with_filter(request):
    """
    To achieve this, we modify the database query to include the filters.
    If any filter is passed, it is added to the DB query.
    If no filter is passed, all tasks are returned.
    """
    filters = {}

    if "completed" in request.query_params:
        filters["completed"] = request.query_params["completed"].lower() == "true"

    if request.query_params.get("title"):
        filters["title__endswith"] = request.query_params["title"]

    tasks = Task.objects.filter(**filters)  # all tasks if filters = {}
    serializer = TaskSerializer(tasks, many=True)
    return Response(serializer.data)
```

`**filters` turns the dict into kwargs: `filter(completed=True, title__endswith="Postgres")`. Empty `{}` returns every task.

Difference from Approach 1: this example uses `title__endswith` (`LIKE '%word'`) instead of `title__icontains` (`ILIKE '%word%'`), and it is a standalone function (no viewset pagination unless you add it).

### Approach 3: `django-filter`

Declare a `FilterSet`. Wire `DjangoFilterBackend` on the viewset. No manual `if` blocks. This is what the project code uses now.

List every `Task` field in `Meta.fields` so each one is a query param. (`fields = "__all__"` skips the PK, so `id` must be listed.) `filter_overrides` keeps text fields on `icontains` so `?title=` still means contains.

**Install:** `pip install django-filter` (`django-filter==26.2` in `requirements.txt`)

**`config/settings.py`:** add `"django_filters"` to `INSTALLED_APPS`.

**`tasks/filters.py`:**

```python
import django_filters
from django.db import models
from .models import Task

class TaskFilter(django_filters.FilterSet):
    class Meta:
        model = Task
        fields = [
            "id", "title", "description", "completed",
            "created_at", "updated_at", "user",
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
```

**`tasks/views.py`:**

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

| URL | SQL idea |
| --- | --- |
| `/api/tasks/?completed=true` | `WHERE completed = true` |
| `/api/tasks/?title=Postgres` | `WHERE title ILIKE '%Postgres%'` |
| `/api/tasks/?description=linked` | `WHERE description ILIKE '%linked%'` |
| `/api/tasks/?user=1` | `WHERE user_id = 1` |
| `/api/tasks/?id=3` | `WHERE id = 3` |
| `/api/tasks/?completed=true&title=Postgres&page=1&page_size=20` | combine fields, then page |

### API call and result (filter)

`GET http://127.0.0.1:8002/api/tasks/?title=Postgres&page=1&page_size=2`

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

`GET http://127.0.0.1:8002/api/tasks/?user=1&page=1&page_size=2` → `count: 801`, first rows id `3` and `4`.

`count` is the filtered total. Pagination still comes from `TaskPagination`. Longer notes: `filtering.md`.

## Why filtering if I already have search?

They are not duplicates.

- **Search** = one text box (`?search=Postgres`). OR across text fields (`title` / `description`). Good for "find anything about this word".
- **Filter** = precise controls per field (`?completed=false`, `?user=1`, `?id=3`). AND across params. Good for status, owner, ids, dates.

`?search=false` does **not** mean "incomplete tasks". `?completed=false` does. `?search=1` does **not** mean "user id 1". `?user=1` does.

Real screens use both: search box + filter dropdowns →  
`/api/tasks/?completed=false&search=API&page=1`

Longer write-up: `search.md` and the top of `filtering.md`.

## Search (easiest): DRF `SearchFilter`

Filter = one param per field (`?title=` + `?completed=`). Search = one param across many fields (`?search=`).

Built into DRF. Add `SearchFilter` next to `DjangoFilterBackend` and set `search_fields`. Older `filter_backends` lines are kept as comments.

```python
from rest_framework.filters import SearchFilter, OrderingFilter

filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
search_fields = ["title", "description"]
```

SQL idea: `WHERE title ILIKE '%word%' OR description ILIKE '%word%'`.

### API call and result (search)

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

`GET http://127.0.0.1:8002/api/tasks/?completed=false&search=API&page=1&page_size=2` → `count: 67`, titles like `Write API tests #1`.

Longer notes: `search.md`.

## Ordering (easiest): DRF `OrderingFilter`

Sort with `?ordering=field` (asc) or `?ordering=-field` (desc). Allow-list in `ordering_fields`. Default when omitted: `ordering = ["id"]`.

```python
from rest_framework.filters import OrderingFilter

filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
ordering_fields = ["id", "title", "completed", "created_at", "updated_at"]
ordering = ["id"]
```

### API call and result (ordering)

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

Combined: `GET http://127.0.0.1:8002/api/tasks/?completed=false&search=API&ordering=-id&page=1&page_size=2` → `count: 67`, ids `994` then `974`.

Longer notes: `ordering.md`.