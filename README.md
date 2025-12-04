BlogProject - Minimal Django blog with:
- Register, Login, Logout
- Create, Update, Delete posts
- Like posts
- Comment on posts

Quick start:
1. Create virtualenv and install requirements.txt
2. python manage.py migrate
3. python manage.py runserver

Admin:
- Create superuser with `python manage.py createsuperuser`


API (Django REST Framework)
Endpoints (after running server):
- /api/posts/  (list, create)
- /api/posts/{id}/  (retrieve, update, delete)
- /api/posts/{id}/like/  (POST to like/unlike)
- /api/comments/  (list, create)
