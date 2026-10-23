from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field

class RegisterIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)

class LoginIn(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: int
    email: EmailStr
    role: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"

class CourseCreate(BaseModel):
    title: str = Field(min_length=2, max_length=200)
    description: str = ""

class CoursePatch(BaseModel):
    title: str | None = Field(default=None, min_length=2, max_length=200)
    description: str | None = None

class CourseOut(BaseModel):
    id: int
    title: str
    description: str
    is_published: bool
    model_config = ConfigDict(from_attributes=True)

class LessonCreate(BaseModel):
    title: str = Field(min_length=2, max_length=200)
    content: str = Field(min_length=1)
    order_index: int = Field(gt=0)

class LessonPatch(BaseModel):
    title: str | None = Field(default=None, min_length=2, max_length=200)
    content: str | None = None
    order_index: int | None = Field(default=None, gt=0)

class LessonOut(BaseModel):
    id: int
    course_id: int
    title: str
    content: str
    order_index: int
    model_config = ConfigDict(from_attributes=True)

class ReorderIn(BaseModel):
    lesson_ids: list[int] = Field(min_length=1)

class EnrollmentOut(BaseModel):
    id: int
    course_id: int
    enrolled_at: datetime
    model_config = ConfigDict(from_attributes=True)

class CourseProgressOut(BaseModel):
    course_id: int
    title: str
    completed_lessons: int
    total_lessons: int
    unfinished_lessons: int
    progress_percent: float
