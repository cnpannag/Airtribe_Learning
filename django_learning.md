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
| GET | `/api/tasks/` | 200 | none. Returns a list. |
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
