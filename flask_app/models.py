from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func
import random

class Note(db.Model):
    #collumns
    id = db.Column(db.Integer, primary_key = True)
    content = db.Column(db.String(128))
    date = db.Column(db.DateTime(timezone = True), default = func.now())
    user = db.Column(db.Integer, db.ForeignKey('user.id'))

def create_secret_key():
    return str(hex(random.randint(0,99999999999)))

class User(db.Model, UserMixin):
    #collumns
    id = db.Column(db.Integer, primary_key = True)
    fname = db.Column(db.String(16))
    lname = db.Column(db.String(16))
    password = db.Column(db.String(64))
    friends = db.Column(db.String, nullable = True)
    alerts = db.Column(db.String(468), default = "")
    secret_key = db.Column(db.String, default = create_secret_key())

    #relationships
    notes = db.relationship('Note')
    image = db.relationship('Img')


class Img(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    mimetype = db.Column(db.Text, nullable=False)
    user = db.Column(db.Integer, db.ForeignKey('user.id'))
