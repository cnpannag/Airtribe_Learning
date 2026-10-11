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



