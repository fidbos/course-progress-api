from fastapi import FastAPI
from app.routers import auth, users, courses, lessons, progress

app = FastAPI(title="Course Progress API", version="1.0.0", description="Kurs, dars va o‘quvchi progressini boshqarish API")
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(courses.router)
app.include_router(lessons.router)
app.include_router(progress.router)

@app.get("/health", tags=["health"])
def health():
    return {"status": "ok"}
