from fastapi import FastAPI

from .routers import projects, users, work_items

app = FastAPI(title="Task Tracker API", version="0.2.0")

app.include_router(users.router)
app.include_router(projects.router)
app.include_router(work_items.router)


@app.get("/health")
def health():
    return {"status": "ok"}
