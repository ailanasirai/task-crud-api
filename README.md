# Task API

A small in-memory CRUD API for managing a to-do list, built with FastAPI. This is Assignment A1 (Week 2) for the FlyRank Backend AI Engineering track.

Data lives only in memory: it resets every time the server restarts. There is no database yet.

## How to run it

```bash
python3 -m venv venv
source venv/bin/activate      # on Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

The API runs at `http://localhost:8000`. Interactive Swagger docs are at `http://localhost:8000/docs`.

## Endpoints

| Method | Path           | Meaning                          |
|--------|----------------|-----------------------------------|
| GET    | `/`            | API info                          |
| GET    | `/health`      | Health check                      |
| GET    | `/tasks`       | List all tasks (supports `?done=` and `?search=`) |
| GET    | `/tasks/{id}`  | Get a single task                 |
| POST   | `/tasks`       | Create a task                     |
| PUT    | `/tasks/{id}`  | Update a task                     |
| DELETE | `/tasks/{id}`  | Delete a task                     |
| GET    | `/stats`       | Task counts (total / done / open) |
| POST   | `/reset`       | Restore the 3 seed tasks          |

## Example request

```bash
curl -i -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title":"Buy milk"}'
```

```
HTTP/1.1 201 Created
content-type: application/json

{"id":4,"title":"Buy milk","done":false}
```

## Status codes

- `200` - successful read/update
- `201` - task created
- `204` - task deleted, no body returned
- `400` - invalid request body (missing or empty title)
- `404` - task id does not exist

## Swagger UI

![Swagger UI screenshot](swagger-screenshot.png)

*(screenshot added after running the app locally and opening /docs)*

## The mortality experiment

Tasks are stored in a plain Python list in memory. When the server restarts, that list is recreated from the 3 seed tasks - any tasks created during the previous run are gone. This is expected: there is no database yet, so nothing survives a restart. This is exactly why Week 3 introduces persistent storage.

## Project structure

```
.
├── main.py           # the API
├── requirements.txt  # dependencies
└── README.md
```
