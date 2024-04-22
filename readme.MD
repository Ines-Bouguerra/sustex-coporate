python -m venv venv

source venv/Scripts/activate

python manage.py runserver

pip freeze > requirements.txt
