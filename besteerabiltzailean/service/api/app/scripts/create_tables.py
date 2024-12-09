from app.model.user_model import User
from app.utils.db import db

from app.service.auth_service import get_password_hash


def create_tables():
    with db:
        db.drop_tables(db.get_tables())
        db.create_tables([User])

def load_default_data():
    admin = User(email="admin@tknika.eus", username="admin", password=get_password_hash("pasahitz_sekretua"), flag="")
    admin.save()
    user = User(email="user@tknika.eus", username="user", password=get_password_hash("pasahitz_sekretua"), flag="No Flag for this user... Maybe for admin;)")
    user.save()

def load_data():
    create_tables()
    load_default_data()