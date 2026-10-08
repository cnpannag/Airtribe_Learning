# HTTP Methods & Request Basics

A quick reference for common HTTP verbs, query/path params, and how they map to typical API work (e.g. accounts and addresses).

---

## Core idea

| Method    | Purpose                         | Idempotent? | Safe? |
|-----------|---------------------------------|-------------|-------|
| GET       | Read a resource                 | Yes         | Yes   |
| HEAD      | Like GET, headers only          | Yes         | Yes   |
| OPTIONS   | Ask what methods are allowed    | Yes         | Yes   |
| POST      | Create a resource (or action)   | No          | No    |
| PUT       | Full replace / upsert           | Yes         | No    |
| PATCH     | Partial update                  | No*         | No    |
| DELETE    | Remove a resource               | Yes         | No    |

\*PATCH *can* be designed to be idempotent, but it is not guaranteed by the HTTP spec the way PUT is.

- **Safe**: should not change server state (read-only).
- **Idempotent**: calling it N times has the same effect as calling it once.

---

## GET — read a resource

Fetch data. No body required (query/path params carry inputs).

**Examples**

```http
GET /accounts/42
GET /accounts?status=active&page=1
```

```bash
curl.exe "http://127.0.0.1:8001/add?a=1&b=2"
```

FastAPI sketch:

```python
@app.get("/accounts/{account_id}")
def get_account(account_id: int):
    return {"id": account_id, "name": "Ada"}
```

---

## POST — create a resource

Create something new. Server usually assigns the id. Sending the same POST twice can create two resources.

**Mental model from notes:** create a new account.

```http
POST /accounts
Content-Type: application/json

{
  "name": "Ada Lovelace",
  "email": "ada@example.com"
}
```

```bash
curl.exe -X POST "http://127.0.0.1:8001/accounts" ^
  -H "Content-Type: application/json" ^
  -d "{\"name\":\"Ada\",\"email\":\"ada@example.com\"}"
```

Typical response: `201 Created` with the new resource (and its id).

---

## PUT — full replacement

Replace the *entire* resource (or create it at a known URL — upsert). Client sends the complete new state.

**Mental model from notes:** attach/replace an address on an existing account by sending the full account (or address) payload again. To “partially” update with PUT, you must resend everything, including unchanged fields.

```http
PUT /accounts/42/address
Content-Type: application/json

{
  "street": "12 Baker Street",
  "city": "London",
  "door": "12A",
  "zip": "NW1"
}
```

If you only wanted to change `door`, with PUT you still send `street`, `city`, `zip`, etc.

```bash
curl.exe -X PUT "http://127.0.0.1:8001/accounts/42/address" ^
  -H "Content-Type: application/json" ^
  -d "{\"street\":\"12 Baker Street\",\"city\":\"London\",\"door\":\"12A\",\"zip\":\"NW1\"}"
```

---

## PATCH — partial update

Change only the fields you send. Unmentioned fields stay as they are.

**Mental model from notes:** change only the door number on an existing account’s address.

```http
PATCH /accounts/42/address
Content-Type: application/json

{
  "door": "12B"
}
```

```bash
curl.exe -X PATCH "http://127.0.0.1:8001/accounts/42/address" ^
  -H "Content-Type: application/json" ^
  -d "{\"door\":\"12B\"}"
```

---

## DELETE — remove a resource

```http
DELETE /accounts/42
```

```bash
curl.exe -X DELETE "http://127.0.0.1:8001/accounts/42"
```

Calling DELETE again on the same id is usually a no-op or `404`; either way the end state is “gone” (idempotent).

---

## HEAD — like GET, but no body

Same URL and headers as GET; response has status/headers only (no payload). Useful to check if a resource exists or for caching (`ETag`, `Content-Length`) without downloading the body.

```http
HEAD /accounts/42
```

```bash
curl.exe -I "http://127.0.0.1:8001/accounts/42"
```

(`-I` sends HEAD.)

---

## OPTIONS — discover allowed methods

Ask the server which verbs are allowed on a URL. Browsers also use OPTIONS for CORS preflight.

```http
OPTIONS /accounts/42
```

Example response headers:

```http
Allow: GET, PUT, PATCH, DELETE, OPTIONS
```

```bash
curl.exe -X OPTIONS "http://127.0.0.1:8001/accounts/42" -i
```

---

## Query parameters vs path parameters vs body

### Path parameters — identify *which* resource

Part of the URL path.

```http
GET /accounts/42
```

`42` is the account id.

```python
@app.get("/accounts/{account_id}")
def get_account(account_id: int):
    ...
```

### Query parameters — filter, sort, paginate, optional inputs

After `?`, as `key=value` pairs joined by `&`.

```http
GET /accounts?status=active&page=2&limit=20
GET /add?a=1&b=2
```

```python
@app.get("/add")
def add(a: float, b: float):
    return {"a": a, "b": b, "sum": a + b}
```

In the browser: `http://127.0.0.1:8001/add?a=1&b=2`

### Request body — create/update payload

Used mainly with POST, PUT, PATCH (JSON is common).

```http
POST /accounts
Content-Type: application/json

{ "name": "Ada", "email": "ada@example.com" }
```

Rule of thumb:

| Where it goes | Typical use                          |
|---------------|--------------------------------------|
| Path          | Resource identity (`/users/5`)       |
| Query         | Filters, search, pagination, flags   |
| Body          | Data to create or update             |

GET/HEAD/DELETE usually avoid bodies; prefer query or path.

---

## PUT vs PATCH (side by side)

Same goal: change door number from `12A` → `12B`.

**PUT** (must send full address):

```json
{
  "street": "12 Baker Street",
  "city": "London",
  "door": "12B",
  "zip": "NW1"
}
```

**PATCH** (only the change):

```json
{
  "door": "12B"
}
```

---

## Account lifecycle example

| Step | Method  | Request                                      | Meaning                          |
|------|---------|----------------------------------------------|----------------------------------|
| 1    | POST    | `/accounts` + name/email                     | Create account                   |
| 2    | GET     | `/accounts/42`                               | Read account                     |
| 3    | PUT     | `/accounts/42/address` + full address        | Set / replace whole address      |
| 4    | PATCH   | `/accounts/42/address` + `{ "door": "12B" }` | Change door only                 |
| 5    | HEAD    | `/accounts/42`                               | Check exists / headers only      |
| 6    | OPTIONS | `/accounts/42`                               | See allowed methods              |
| 7    | DELETE  | `/accounts/42`                               | Remove account                   |

---

## Other verbs you may see

| Method   | Notes |
|----------|--------|
| TRACE    | Echo request for diagnostics; rare and often disabled. |
| CONNECT  | Used by proxies for HTTPS tunnels; not typical in REST APIs. |

For everyday REST/FastAPI work, focus on: **GET, POST, PUT, PATCH, DELETE**, plus **HEAD** and **OPTIONS**.

---

## Quick checklist

1. **Reading?** → GET (or HEAD if you only need headers).
2. **Creating with server-generated id?** → POST.
3. **Replacing the whole resource?** → PUT.
4. **Changing a few fields?** → PATCH.
5. **Removing?** → DELETE.
6. **What can I call on this URL?** → OPTIONS.
7. **Filters / pagination?** → query params (`?page=1&status=active`).
8. **Which item?** → path param (`/accounts/42`).
