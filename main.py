from ast import Delete
from fastapi import FastAPI, Request
from pydantic import PostgresDsn

app = FastAPI()
# **Query parameters** --> more flexible, it will work even if we add extra parameters like c=4
# http://127.0.0.1:8001/add?c=4&a=1&b=2
@app.get("/add")
def add(a: float, b: float):
    return {"a":a,"b":b,"sum":a+b,"message":"From Query Parameters"}


# **Path Parameters** --> Rigid, URL has to be exact for this to work
# http://127.0.0.1:8001/add/path/1/2 --> will work
# http://127.0.0.1:8001/add/path/1/2/3 --> wont work
@app.get("/add/path/{a}/{b}")
def add(a:float, b:float):
    return {"a":a,"b":b,"sum":a+b,"message":"From Path Parameters"}


@app.get("/user/{user_id}")
def get_user(user_id: int):
    return {"user_id":user_id, "name":"test"} #you can add any other details you need like age, addr, etc
# No need to add it anywhere else
# http://127.0.0.1:8001/user/1
# {"user_id":1,"name":"test"}

# **post**
@app.post("/user")
def create_user(user: dict):
    return {"user_id":user["user_id"], "name":user["name"]}
# http://127.0.0.1:8001/user
# in post >> body >>  raw >> json
# {
#     "user_id":"123",
#     "name":"test123"

# }


# output:
# {
# 	"user_id": "123",
# 	"name": "test123"
# }



# **headers**
#if we dont put test or something else here it will run the above since it cannot understand the variable
@app.get("/user/test/headers") 
def get_user_headers(request:Request):
    headers_dict=dict(request.headers)
    print("Recieved headers:",headers_dict) # this will print in terminal logs below for debugging
    return{"headers":headers_dict}
# get http://127.0.0.1:8001/user/test/headers
# >> headers tab >> test: test, name xcv
# {"headers":{"accept":"*/*","accept-encoding":"gzip, deflate, br","user-agent":"EchoapiRuntime/1.1.0","connection":"keep-alive","test":"test","name":"xcv","content-type":"application/json","cache-control":"no-cache","host":"127.0.0.1:8001","content-length":"50"}}

# Terminal logs
# INFO:     Waiting for application startup.
# INFO:     Application startup complete.
# Recieved headers: {'accept': '*/*', 'accept-encoding': 'gzip, deflate, br', 'user-agent': 'EchoapiRuntime/1.1.0', 'connection': 'keep-alive', 'test': 'test', 'name': 'xcv', 'content-type': 'application/json', 'cache-control': 'no-cache', 'host': '127.0.0.1:8001', 'content-length': '50'}
# INFO:     127.0.0.1:63509 - "GET /user/test/headers HTTP/1.1" 200 OK
# **note** 


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