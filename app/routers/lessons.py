from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import get_current_user, require_admin
from app.models import Course, Lesson, Enrollment, User
from app.schemas import LessonPatch, LessonOut, ReorderIn

router = APIRouter(tags=["lessons"])

def ensure_enrolled(db: Session, user_id: int, course_id: int):
    enrolled = db.query(Enrollment).filter_by(user_id=user_id, course_id=course_id).first()
    if not enrolled:
        raise HTTPException(status_code=403, detail="Bu kursga yozilmagansiz")

@router.get("/courses/{course_id}/lessons", response_model=list[LessonOut])
def course_lessons(course_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    course = db.get(Course, course_id)
    if not course or not course.is_published: raise HTTPException(404, "Kurs topilmadi")
    ensure_enrolled(db, user.id, course_id)
    return db.query(Lesson).filter_by(course_id=course_id).order_by(Lesson.order_index).all()

@router.get("/lessons/{lesson_id}", response_model=LessonOut)
def lesson_detail(lesson_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    lesson = db.get(Lesson, lesson_id)
    if not lesson: raise HTTPException(404, "Dars topilmadi")
    if not lesson.course.is_published: raise HTTPException(404, "Dars topilmadi")
    ensure_enrolled(db, user.id, lesson.course_id)
    return lesson

@router.patch("/lessons/{lesson_id}", response_model=LessonOut)
def update_lesson(lesson_id: int, data: LessonPatch, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    lesson = db.get(Lesson, lesson_id)
    if not lesson: raise HTTPException(404, "Dars topilmadi")
    if lesson.course.is_published: raise HTTPException(409, "E’lon qilingan kurs darslari o‘zgartirilmaydi")
    for key, value in data.model_dump(exclude_unset=True).items(): setattr(lesson, key, value)
    try: db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "Bu tartib raqami kursda band")
    db.refresh(lesson)
    return lesson

@router.delete("/lessons/{lesson_id}", status_code=204)
def delete_lesson(lesson_id: int, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    lesson = db.get(Lesson, lesson_id)
    if not lesson: raise HTTPException(404, "Dars topilmadi")
    if lesson.course.is_published: raise HTTPException(409, "E’lon qilingan kurs darslari o‘zgartirilmaydi")
    db.delete(lesson); db.commit()

@router.put("/courses/{course_id}/lessons/reorder", response_model=list[LessonOut])
def reorder_lessons(course_id: int, data: ReorderIn, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    course = db.get(Course, course_id)
    if not course: raise HTTPException(404, "Kurs topilmadi")
    if course.is_published: raise HTTPException(409, "E’lon qilingan kurs tartibi o‘zgartirilmaydi")
    lessons = db.query(Lesson).filter_by(course_id=course_id).all()
    by_id = {lesson.id: lesson for lesson in lessons}
    if len(data.lesson_ids) != len(set(data.lesson_ids)) or set(data.lesson_ids) != set(by_id):
        raise HTTPException(422, "lesson_ids kursdagi barcha dars IDlarini bir martadan o‘z ichiga olishi kerak")
    # Avval mavjud tartib raqamlaridan kattaroq vaqtinchalik raqamlar beriladi.
    # Bu unique va CHECK(order_index > 0) cheklovlarini buzmaydi.
    max_order = max((lesson.order_index for lesson in lessons), default=0)
    for i, lesson_id in enumerate(data.lesson_ids, start=1):
        by_id[lesson_id].order_index = max_order + i
    db.flush()
    for i, lesson_id in enumerate(data.lesson_ids, start=1):
        by_id[lesson_id].order_index = i
    db.commit()
    return db.query(Lesson).filter_by(course_id=course_id).order_by(Lesson.order_index).all()
