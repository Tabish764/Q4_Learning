from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, constr, EmailStr, field_validator
from datetime import date

app = FastAPI()

users_db = {}
tasks_db = {}

class NewUser(BaseModel):
    username: constr(min_length=3, max_length=20)
    email: EmailStr

class UserProfile(BaseModel):
    id: int
    username: str
    email: EmailStr

class TaskDetails(BaseModel):
    id: int
    title: str
    description: str
    status: str
    due_date: date
    user_id: int

class NewTask(BaseModel):
    title: str
    description: str
    status: str
    due_date: date
    user_id: int

    @field_validator("due_date")
    def validate_due_date(cls, v):
        if v < date.today():
            raise ValueError("Due date must be today or in the future")
        return v

class StatusUpdate(BaseModel):
    status: str

@app.post("/users/", response_model=UserProfile)
def register_user(payload: NewUser):
    user_id = max(users_db.keys(), default=0) + 1
    new_profile = UserProfile(id=user_id, username=payload.username, email=payload.email)
    users_db[user_id] = new_profile
    return new_profile

@app.get("/users/{uid}", response_model=UserProfile)
def fetch_user(uid: int):
    user = users_db.get(uid)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.post("/tasks/", response_model=TaskDetails)
def create_task(payload: NewTask):
    task_id = max(tasks_db.keys(), default=0) + 1
    task_entry = TaskDetails(id=task_id, **payload.dict())
    tasks_db[task_id] = task_entry
    return task_entry

@app.get("/tasks/{tid}", response_model=TaskDetails)
def get_task(tid: int):
    task = tasks_db.get(tid)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@app.put("/tasks/{tid}", response_model=TaskDetails)
def modify_task_status(tid: int, update: StatusUpdate):
    valid_states = {"pending", "in_progress", "completed"}

    task = tasks_db.get(tid)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if update.status not in valid_states:
        raise HTTPException(status_code=400, detail="Invalid task status")

    task.status = update.status
    return task

@app.get("/users/{uid}/tasks", response_model=list[TaskDetails])
def list_user_tasks(uid: int):
    if uid not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    return [task for task in tasks_db.values() if task.user_id == uid]
