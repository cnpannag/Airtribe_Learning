# Airtribe_Learning

POST http://127.0.0.1:8002/reporters/

{
    "name":"Pannag", 
    "email":"P@ATB.com", 
    "team":"Student"
}
{
	"id": 1,
	"name": "Pannag",
	"email": "P@ATB.com",
	"team": "Student",
	"created_at": "2026-10-10T19:16:47.426696Z",
	"updated_at": "2026-10-10T19:16:47.426696Z"
}

------------------

GET http://127.0.0.1:8002/reporters/
[
	{
		"id": 1,
		"name": "Pannag",
		"email": "P@ATB.com",
		"team": "Student",
		"created_at": "2026-10-10T19:16:47.426696Z",
		"updated_at": "2026-10-10T19:16:47.426696Z"
	},
	{
		"id": 2,
		"name": "Pannag_2",
		"email": "P2@ATB.com",
		"team": "Student",
		"created_at": "2026-10-10T19:19:21.482877Z",
		"updated_at": "2026-10-10T19:19:21.482877Z"
	}
]



----------------------------
GET http://127.0.0.1:8002/reporters/1

{
	"id": 1,
	"name": "Pannag",
	"email": "P@ATB.com",
	"team": "Student",
	"created_at": "2026-10-10T19:16:47.426696Z",
	"updated_at": "2026-10-10T19:16:47.426696Z"
}


--------------------------------


POST localhost:8002/issues/

{
     "title": "critical issue", 
     "description": "testing a critical isssue here", 
     "status": "open", 
     "priority": "critical", 
     "reporter":"1"
}

[
	{
		"id": 1,
		"title": "critical issue",
		"description": "testing a critical isssue here",
		"status": "open",
		"priority": "critical",
		"reporter": 1,
		"created_at": "2026-10-11T16:48:41.787756Z",
		"updated_at": "2026-10-11T16:48:41.787756Z"
	}
]




-----------------------------
GET localhost:8002/issues/

[
	{
		"id": 1,
		"title": "critical issue",
		"description": "testing a critical isssue here",
		"status": "open",
		"priority": "critical",
		"reporter": 1,
		"created_at": "2026-10-11T16:48:41.787756Z",
		"updated_at": "2026-10-11T16:48:41.787756Z"
	},
	{
		"id": 2,
		"title": "Low priority issue",
		"description": "testing a low priority isssue here",
		"status": "open",
		"priority": "low",
		"reporter": 1,
		"created_at": "2026-10-11T16:51:14.917921Z",
		"updated_at": "2026-10-11T16:51:14.917921Z"
	}
]



-------------------------
POST localhost:8002/issues/

{
     "title": "", 
     "description": "testing a low priority isssue here", 
     "status": "", 
     "priority": "low", 
     "reporter":"1"
}


{
	"title": [
		"This field may not be blank."
	],
	"status": [
		"This field may not be blank."
	]
}


--------------------------

Either missed in class or by me so implemented with AI. 
Not sure if the implementation is correct to add logic in models.py and import in views.py

Added in models.py since project structre mentions 
"models.py      # your OOP classes go here" 
and 
"issues/models.py" in Part A

-------------------------------

localhost:8002/issues/1/describe/
{
	"summary": "[URGENT] critical issue — needs immediate attention"
}

localhost:8002/issues/2/describe/
{
	"summary": "Low priority issue — low priority, handle when free"
}
