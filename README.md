# Course Progress API — FastAPI imtihon loyihasi

Bu loyiha FastAPI + PostgreSQL + SQLAlchemy + Alembic + JWT bilan yozilgan. Swagger orqali tekshiriladi.

## 1. Kompyuterda ishga tushirish (Windows PowerShell)

ZIPni oching, so‘ng loyiha papkasiga kiring:
```powershell
cd course_progress_api
py -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```
`.env` ichida `DATABASE_URL` ni PostgreSQL'dagi o‘zingiz yaratgan baza, foydalanuvchi va parolga moslang. Masalan:
`postgresql+psycopg://course_user:parol@localhost:5432/course_db`

PostgreSQL'da baza va foydalanuvchi yarating (psql yoki pgAdmin orqali):
```sql
CREATE USER course_user WITH PASSWORD 'parol';
CREATE DATABASE course_db OWNER course_user;
```
Keyin:
```powershell
alembic upgrade head
uvicorn app.main:app --reload
```
Brauzerda `http://127.0.0.1:8000/docs` ni oching. `GET /health` ishlashini tekshiring.

## 2. Admin yaratish

Oddiy register har doim `student` rolini beradi. Birinchi adminni qo‘lda yarating:
```powershell
python -m app.create_admin
```
Terminal so‘rovlariga email va parol kiriting. Admin mavjud bo‘lsa, script uni qayta yaratmaydi.

## 3. Imtihonda namoyish qilish

1. `/auth/register` orqali 2 ta student yarating.
2. `/auth/login` orqali admin sifatida token oling va Swagger'da **Authorize** tugmasiga `Bearer TOKEN` kiriting.
3. Admin `/courses` orqali kurs yaratsin (`title`, `description`).
4. Admin `/courses/{course_id}/lessons` orqali 4 ta dars qo‘shsin. `order_index` qiymatlari 1, 2, 3, 4 bo‘lsin.
5. Admin `/courses/{course_id}/publish` bilan kursni e’lon qilsin.
6. Student A tokeni bilan `/courses` ro‘yxatidan kursni topib `/courses/{course_id}/enroll` ga POST qilsin.
7. Student A `/my/courses` ni ko‘rsin — progress 0%, tugallanmagan 4.
8. Student A `/courses/{course_id}/lessons` orqali darslarni ko‘rsin. Birinchi darsni `POST /lessons/{lesson_id}/complete` orqali tugatsin.
9. `/my/courses` ni qayta ko‘ring: progress 25%, tugallanmagan 3.
10. Xuddi shu complete so‘rovini qayta yuboring: progress hanuz 25%.
11. Student B kursga yozilmasdan turib `/courses/{course_id}/lessons` yoki `GET /lessons/{lesson_id}` ni chaqirsin: 403 yoki maxfiy obyekt uchun 404.
12. Draft kursni publish qilib ko‘ring: dars yo‘q bo‘lsa 409.

**Muhim:** Swagger'da har bir foydalanuvchi uchun `/auth/login` qilib, tokenni `Authorize` orqali almashtiring.

## 4. GitHub

GitHub'da yangi repository oching. Loyiha ichidan:
```bash
git init
git add .
git commit -m "Initial course progress API"
git branch -M main
git remote add origin https://github.com/USERNAME/REPOSITORY.git
git push -u origin main
```
`USERNAME/REPOSITORY` ni o‘zingizning repository manzilingizga almashtiring. `.env` gitignore'da; uni hech qachon GitHub'ga yubormang.

## 5. EC2 deploy

Deploy fayllari `deploy/` papkasida namunaviy qilib berilgan. `deploy/DEPLOY.md` ni o‘qing. EC2 uchun Ubuntu server, PostgreSQL, Python, Nginx, systemd va GitHub Actions secrets (`EC2_HOST`, `EC2_SSH_KEY`) sozlanishi kerak. `.github/workflows/deploy.yml` testlar muvaffaqiyatli bo‘lgandagina deploy job'ini ishga tushiradi. GitHub repository settings'da Actions secrets sozlanmaguncha avtomatik deploy ishlamaydi.

## API qisqacha

- `POST /auth/register`, `POST /auth/login`, `GET /users/me`
- `GET /courses?search=python&skip=0&limit=20`
- `GET /courses/{id}` — faqat published kurs
- `POST /courses` — admin
- `PATCH /courses/{id}` va `DELETE /courses/{id}` — faqat draft kurs admin tomonidan
- `POST /courses/{id}/publish` — admin, kamida bitta dars kerak
- `POST /courses/{id}/lessons`, `PATCH /lessons/{id}`, `DELETE /lessons/{id}`, `PUT /courses/{id}/lessons/reorder` — admin; published kurs o‘zgarmaydi
- `POST /courses/{id}/enroll`
- `GET /courses/{id}/lessons` va `GET /lessons/{id}` — enrolled student
- `POST /lessons/{id}/complete` — enrolled student
- `GET /my/courses` — o‘z kurslari va progressi
- `GET /health`

Progress = tugatilgan darslar / jami darslar × 100, 2 xonagacha yaxlitlanadi. Enrollment va LessonProgress uchun DB unique cheklovlari bor.
