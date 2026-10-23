from getpass import getpass
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import User
from app.security import hash_password

def main():
    email = input("Admin email: ").strip().lower()
    password = getpass("Admin parol (kamida 8 belgi): ")
    if len(password) < 8:
        print("Parol kamida 8 belgidan iborat bo‘lsin."); return
    db: Session = SessionLocal()
    try:
        if db.query(User).filter_by(email=email).first():
            print("Bu email mavjud. Mavjud foydalanuvchi o‘zgartirilmadi."); return
        db.add(User(email=email, password_hash=hash_password(password), role="admin"))
        db.commit()
        print("Admin yaratildi. Endi /auth/login orqali kiring.")
    finally:
        db.close()

if __name__ == "__main__":
    main()
