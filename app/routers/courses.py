from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import get_current_user, require_admin
from app.models import Course, Lesson, Enrollment, User
from app.schemas import CourseCreate, CoursePatch, CourseOut, LessonCreate, LessonOut, EnrollmentOut

router = APIRouter(tags=["courses"])

@router.get("/courses", response_model=list[CourseOut])
def list_courses(search: str | None = None, skip: int = Query(0, ge=0), limit: int = Query(20, ge=1, le=100), db: Session = Depends(get_db)):
    q = db.query(Course).filter(Course.is_published.is_(True))
    if search:
        q = q.filter(Course.title.ilike(f"%{search}%"))
    return q.order_by(Course.id).offset(skip).limit(limit).all()

@router.get("/courses/{course_id}", response_model=CourseOut)
def course_detail(course_id: int, db: Session = Depends(get_db)):
    course = db.get(Course, course_id)
    if not course or not course.is_published:
        raise HTTPException(status_code=404, detail="E’lon qilingan kurs topilmadi")
    return course

@router.post("/courses", response_model=CourseOut, status_code=201)
def create_course(data: CourseCreate, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    course = Course(title=data.title, description=data.description, is_published=False)
    db.add(course); db.commit(); db.refresh(course)
    return course

@router.patch("/courses/{course_id}", response_model=CourseOut)
def update_course(course_id: int, data: CoursePatch, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    course = db.get(Course, course_id)
    if not course: raise HTTPException(404, "Kurs topilmadi")
    if course.is_published: raise HTTPException(409, "E’lon qilingan kurs o‘zgartirilmaydi")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(course, key, value)
    db.commit(); db.refresh(course)
    return course

@router.delete("/courses/{course_id}", status_code=204)
def delete_course(course_id: int, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    course = db.get(Course, course_id)
    if not course: raise HTTPException(404, "Kurs topilmadi")
    if course.is_published: raise HTTPException(409, "E’lon qilingan kurs o‘chirilmaydi")
    if db.query(Enrollment).filter_by(course_id=course_id).first():
        raise HTTPException(409, "Yozilish tarixi bor kursni o‘chirib bo‘lmaydi")
    db.delete(course); db.commit()

@router.post("/courses/{course_id}/publish", response_model=CourseOut)
def publish_course(course_id: int, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    course = db.get(Course, course_id)
    if not course: raise HTTPException(404, "Kurs topilmadi")
    if db.query(Lesson).filter_by(course_id=course_id).count() < 1:
        raise HTTPException(409, "Kursni e’lon qilish uchun kamida bitta dars kerak")
    course.is_published = True
    db.commit(); db.refresh(course)
    return course

@router.post("/courses/{course_id}/lessons", response_model=LessonOut, status_code=201)
def add_lesson(course_id: int, data: LessonCreate, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    course = db.get(Course, course_id)
    if not course: raise HTTPException(404, "Kurs topilmadi")
    if course.is_published: raise HTTPException(409, "E’lon qilingan kurs darslari o‘zgartirilmaydi")
    lesson = Lesson(course_id=course_id, **data.model_dump())
    db.add(lesson)
    try: db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "Bu tartib raqami kursda band")
    db.refresh(lesson)
    return lesson

@router.post("/courses/{course_id}/enroll", response_model=EnrollmentOut, status_code=201)
def enroll(course_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    course = db.get(Course, course_id)
    if not course or not course.is_published: raise HTTPException(404, "E’lon qilingan kurs topilmadi")
    enrollment = Enrollment(user_id=user.id, course_id=course_id)
    db.add(enrollment)
    try: db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "Siz bu kursga oldin yozilgansiz")
    db.refresh(enrollment)
    return enrollment
