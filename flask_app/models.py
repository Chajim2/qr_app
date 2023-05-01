from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func

class Note(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    content = db.Column(db.String(128))
    date = db.Column(db.DateTime(timezone = True), default = func.now())
    user = db.Column(db.Integer, db.ForeignKey('user.id'))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key = True)
    fname = db.Column(db.String(16))
    lname = db.Column(db.String(16))
    password = db.Column(db.String(64))
    notes = db.relationship('Note')
