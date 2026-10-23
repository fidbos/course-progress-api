from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import get_current_user
from app.models import Course, Lesson, Enrollment, LessonProgress, User
from app.schemas import CourseProgressOut

router = APIRouter(tags=["progress"])

@router.post("/lessons/{lesson_id}/complete")
def complete_lesson(lesson_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    lesson = db.get(Lesson, lesson_id)
    if not lesson or not lesson.course.is_published:
        raise HTTPException(404, "Dars topilmadi")
    enrollment = db.query(Enrollment).filter_by(user_id=user.id, course_id=lesson.course_id).first()
    if not enrollment:
        raise HTTPException(403, "Bu kursga yozilmagansiz")
    existing = db.query(LessonProgress).filter_by(enrollment_id=enrollment.id, lesson_id=lesson_id).first()
    if existing:
        return {"message": "Dars oldin tugatilgan", "completed": True, "already_completed": True}
    db.add(LessonProgress(enrollment_id=enrollment.id, lesson_id=lesson_id))
    try: db.commit()
    except IntegrityError:
        db.rollback()
        return {"message": "Dars oldin tugatilgan", "completed": True, "already_completed": True}
    return {"message": "Dars tugatildi", "completed": True, "already_completed": False}

@router.get("/my/courses", response_model=list[CourseProgressOut])
def my_courses(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    enrollments = db.query(Enrollment).filter_by(user_id=user.id).all()
    results = []
    for enrollment in enrollments:
        course = db.get(Course, enrollment.course_id)
        total = db.query(Lesson).filter_by(course_id=course.id).count()
        completed = (db.query(LessonProgress).join(Enrollment, LessonProgress.enrollment_id == Enrollment.id)
                     .join(Lesson, LessonProgress.lesson_id == Lesson.id)
                     .filter(Enrollment.id == enrollment.id, Lesson.course_id == course.id).count())
        percent = round(min(100.0, completed / total * 100), 2) if total else 0.0
        results.append({"course_id": course.id, "title": course.title, "completed_lessons": completed,
                        "total_lessons": total, "unfinished_lessons": max(0, total - completed),
                        "progress_percent": percent})
    return results
