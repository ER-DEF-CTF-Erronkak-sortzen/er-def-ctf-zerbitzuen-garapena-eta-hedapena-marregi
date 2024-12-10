import peewee

from app.utils.db import db

class User(peewee.Model):
    email = peewee.CharField(unique=True, index=True)
    username = peewee.CharField(unique=True, index=True)
    password = peewee.CharField()
    flag = peewee.TextField()

    class Meta:
        database = db