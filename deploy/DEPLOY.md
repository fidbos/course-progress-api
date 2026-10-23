# EC2 deploy qo‘llanmasi

Bu fayllar deploy konfiguratsiyasi namunasi. EC2 akkaunt/server va GitHub secretsni egasi o‘zi sozlashi kerak.

1. Ubuntu EC2 yarating, security group'da SSH (faqat o‘z IP'ingiz) va HTTP 80 oching.
2. Serverga SSH orqali kiring va o‘rnating:
   ```bash
   sudo apt update
   sudo apt install -y python3-venv python3-pip postgresql postgresql-contrib nginx git
   ```
3. PostgreSQL'da `course_user` va `course_db` yarating. `.env` uchun kuchli `SECRET_KEY` belgilang.
4. Repository'ni `/var/www/course_progress_api` ichiga clone qiling. `venv` yarating, `pip install -r requirements.txt`, `.env` yarating va `alembic upgrade head` bajaring.
5. Xizmat:
   ```bash
   sudo cp deploy/course-progress-api.service /etc/systemd/system/
   sudo chown -R www-data:www-data /var/www/course_progress_api
   sudo systemctl daemon-reload
   sudo systemctl enable --now course-progress-api
   ```
6. Nginx:
   ```bash
   sudo cp deploy/nginx-course-progress.conf /etc/nginx/sites-available/course-progress-api
   sudo ln -s /etc/nginx/sites-available/course-progress-api /etc/nginx/sites-enabled/course-progress-api
   sudo nginx -t
   sudo systemctl reload nginx
   ```
7. GitHub repository Settings → Secrets and variables → Actions ichida `EC2_HOST` (public IPv4/DNS) va `EC2_SSH_KEY` (private SSH key matni) qo‘shing. Private keyni hech qachon repository'ga qo‘ymang.
8. GitHub Actions deploy ishlashi uchun serverda repository `/var/www/course_progress_api` yo‘lida bo‘lishi va `ubuntu` foydalanuvchisi `sudo systemctl restart course-progress-api` ni parolsiz bajarish huquqiga ega bo‘lishi kerak. Bu sudoers qoidasini ehtiyotkorlik bilan, faqat shu servisga cheklab sozlang.
9. `http://EC2_PUBLIC_IP/health` va `/docs` ni ochib tekshiring. HTTPS uchun domen va TLS sertifikat (masalan, Certbot) qo‘shing.

Eslatma: bu deploy namunasi EC2'ga real ulanish qilmaydi va AWS resurslarini avtomatik yaratmaydi. Qabul sharti uchun o‘z GitHub repository'ingiz va haqiqiy EC2 deploy'ni bajarish zarur.
