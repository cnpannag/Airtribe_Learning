from fastapi import FastAPI

app = FastAPI()

@app.get("/add")
def add(a: float, b: float):
    return {"a":a,"b":b,"sum":a+b}

add(1,2)

# run in terminal
# uvicorn main:app --reload --port 8001
# curl.exe "http://127.0.0.1:8001/add?a=1&b=2"
# or open in browser : http://127.0.0.1:8001/add?a=1&b=2