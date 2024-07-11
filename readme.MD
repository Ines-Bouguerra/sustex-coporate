python -m venv venv

source venv/Scripts/activate

python manage.py runserver

pip freeze > requirements.txt

## cmd to init model in local 
python manage.py init_model
