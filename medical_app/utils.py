import json, hashlib
from medical_app.models import User
from medical_app import db


def read_data(path='./medical_app/config.json'):
    with open(path, encoding='utf-8') as f:
        return json.load(f)


def add_user(email, username, password, avatar):
    password = str(hashlib.md5(password.encode('utf-8')).hexdigest())
    u = User(
             email=email,
             username=username,
             password=password,
             avatar=avatar)
    try:
        db.session.add(u)
        db.session.commit()

        return True
    except Exception as ex:
        print(ex)
        return False