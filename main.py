"""
Task API - a small CRUD API for managing a to-do list.
Built for FlyRank Backend AI Engineering Track, Week 2, Assignment A1.

Data lives in memory only - it resets whenever the server restarts.
Run with: uvicorn main:app --reload
Docs at:  http://localhost:8000/docs
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, field_validator
from typing import Optional

app = FastAPI(
    title="Task API",
    version="1.0",
    description="A small in-memory CRUD API for managing a to-do list.",
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    FastAPI/Pydantic return 422 for bad request bodies by default.
    This assignment asks for 400 (Bad Request) instead, so we translate it here.
    """
    first_error = exc.errors()[0]
    field = ".".join(str(loc) for loc in first_error["loc"] if loc != "body")
    return JSONResponse(
        status_code=400,
        content={"error": f"Invalid request body: {field} - {first_error['msg']}"},
    )


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------

class Task(BaseModel):
    id: int
    title: str
    done: bool = False


class TaskCreate(BaseModel):
    title: str

    @field_validator("title")
    @classmethod
    def title_must_not_be_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("title must not be empty")
        return v


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    done: Optional[bool] = None

    @field_validator("title")
    @classmethod
    def title_must_not_be_empty_if_present(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.strip():
            raise ValueError("title must not be empty")
        return v


# ---------------------------------------------------------------------------
# In-memory "database"
# ---------------------------------------------------------------------------

def seed_tasks() -> list[dict]:
    return [
        {"id": 1, "title": "Buy groceries", "done": False},
        {"id": 2, "title": "Write project README", "done": False},
        {"id": 3, "title": "Push code to GitHub", "done": True},
    ]


tasks: list[dict] = seed_tasks()
next_id: int = 4


# ---------------------------------------------------------------------------
# Stage 1 - root and health
# ---------------------------------------------------------------------------

@app.get("/", tags=["meta"], summary="API info")
def read_root():
    """Describes the API and lists its main endpoints."""
    return {
        "name": "Task API",
        "version": "1.0",
        "endpoints": ["/tasks", "/tasks/{id}", "/health", "/stats"],
    }


@app.get("/health", tags=["meta"], summary="Health check")
def health_check():
    """Used to confirm the server is alive."""
    return {"status": "ok"}


# ---------------------------------------------------------------------------
# Stage 2 - read
# ---------------------------------------------------------------------------

@app.get("/tasks", tags=["tasks"], summary="List tasks")
def list_tasks(done: Optional[bool] = None, search: Optional[str] = None):
    """
    Returns all tasks. Supports two optional query parameters:
    - done: filter to only tasks matching this done state
    - search: filter to tasks whose title contains this text (case-insensitive)
    """
    result = tasks
    if done is not None:
        result = [t for t in result if t["done"] == done]
    if search:
        needle = search.lower()
        result = [t for t in result if needle in t["title"].lower()]
    return result


@app.get("/tasks/{task_id}", tags=["tasks"], summary="Get one task")
def get_task(task_id: int):
    """Returns a single task by id, or 404 if it does not exist."""
    for t in tasks:
        if t["id"] == task_id:
            return t
    raise HTTPException(status_code=404, detail=f"Task {task_id} not found")


# ---------------------------------------------------------------------------
# Stage 3 - create
# ---------------------------------------------------------------------------

@app.post("/tasks", status_code=201, tags=["tasks"], summary="Create a task")
def create_task(payload: TaskCreate):
    """Creates a new task with the given title. done defaults to false."""
    global next_id
    new_task = {"id": next_id, "title": payload.title.strip(), "done": False}
    tasks.append(new_task)
    next_id += 1
    return new_task


# ---------------------------------------------------------------------------
# Stage 4 - update and delete
# ---------------------------------------------------------------------------

@app.put("/tasks/{task_id}", tags=["tasks"], summary="Update a task")
def update_task(task_id: int, payload: TaskUpdate):
    """Replaces a task's title and/or done state. 404 if the task does not exist."""
    for t in tasks:
        if t["id"] == task_id:
            if payload.title is not None:
                t["title"] = payload.title.strip()
            if payload.done is not None:
                t["done"] = payload.done
            return t
    raise HTTPException(status_code=404, detail=f"Task {task_id} not found")


@app.delete("/tasks/{task_id}", status_code=204, tags=["tasks"], summary="Delete a task")
def delete_task(task_id: int):
    """Removes a task. 404 if the task does not exist. Returns no content on success."""
    for i, t in enumerate(tasks):
        if t["id"] == task_id:
            tasks.pop(i)
            return
    raise HTTPException(status_code=404, detail=f"Task {task_id} not found")


# ---------------------------------------------------------------------------
# Extras - stats and reset
# ---------------------------------------------------------------------------

@app.get("/stats", tags=["extras"], summary="Task statistics")
def get_stats():
    """Returns counts computed from the current task list."""
    total = len(tasks)
    done_count = sum(1 for t in tasks if t["done"])
    return {"total": total, "done": done_count, "open": total - done_count}


@app.post("/reset", tags=["extras"], summary="Reset to seed data")
def reset_tasks():
    """Restores the 3 original example tasks. Handy for demos and testing."""
    global tasks, next_id
    tasks = seed_tasks()
    next_id = 4
    return {"status": "reset", "tasks": tasks}
