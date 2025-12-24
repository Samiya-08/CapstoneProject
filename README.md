News Magazine API
Yangiliklar sayti uchun Django REST Framework backend.
🚀 O'rnatish
1. Klonlash
bashgit clone <repo-url>
cd CapstoneProject
2. Virtual environment

bashpython -m venv .venv
source .venv/bin/activate  

3. Paketlarni o'rnatish
   
bashpip install -r requirements.txt

5. Database yaratish

bashpython manage.py migrate
python manage.py createsuperuser

7. Serverni ishga tushirish

bashpython manage.py runserver


📍 Linklar

Swagger: http://localhost:8000/swagger/
Admin: http://localhost:8000/admin/

🔐 Login
POST /auth/login/
json{
  "username": "admin",
  "password": "admin123"
}
Natija:
json{
  "access": "token...",
  "refresh": "token..."
}
