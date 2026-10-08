from ast import Delete
from fastapi import FastAPI
from pydantic import PostgresDsn

app = FastAPI()

@app.get("/add")
def add(a: float, b: float):
    return {"a":a,"b":b,"sum":a+b}

add(1,2)


# GET
# post: create a resource --> create a new account
# put : updating a resource --> full replacement happens --> create an address to existing account
# to do a partial update using put, you need to send all the details again with the updated addr which essentially is updating everything 
# Delete
# PATCH: partially updating a resource --> only an update happens --> changing the door number of an existing account
# Query: send values to filter the data before retreiving
# header: values that are sent but cannot be seen in the url like authorisation tokens, headers can be seen on going to inspect but not on the url line 


# run in terminal
# uvicorn main:app --reload --port 8001
# or 
# python -m uvicorn main:app --reload --port 8001                                     
# curl.exe "http://127.0.0.1:8001/add?a=1&b=2"
# or open in browser : http://127.0.0.1:8001/add?a=1&b=2


# Fix
# 1. Stop the current server (Ctrl+C).

# 2. Run uvicorn through the venv Python, so it cannot pick Anaconda:

# .\.venv\Scripts\python.exe -m uvicorn main:app --reload --port 8001
# 3. If that still fails, install matching packages in the venv:

# .\.venv\Scripts\python.exe -m pip install -U "fastapi" "uvicorn[standard]"
# Then start it again with the same python.exe -m uvicorn command.

# 4. Confirm which interpreter is running:

# Get-Command uvicorn | Select-Object Source
# .\.venv\Scripts\python.exe -c "import fastapi, starlette, sys; print(sys.executable); print(fastapi.__version__); print(starlette.__version__); print(fastapi.__file__)"
# sys.executable and fastapi.__file__ should both live under .venv, not anaconda3.