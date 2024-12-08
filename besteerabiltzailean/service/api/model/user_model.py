import peewee

from api.utils.db import db

class User(peewee.Model):
    email = peewee.CharField(unique=True, index=True)
    username = peewee.CharField(unique=True, index=True)
    password = peewee.CharField()
    flag = peewee.CharField(unique=True)

    class Meta:
        database = db