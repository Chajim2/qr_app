from flask import Blueprint, render_template, request, jsonify
from .models import Note
from. import db
from flask_login import login_required, current_user
from sqlalchemy.sql import func
import json

views = Blueprint('views',__name__)

@views.route('/', methods = ["POST","GET"])
@login_required
def home():
    text = request.form.get('note')
    if request.method == 'POST':
        new_note = Note(content = text, date = func.now(), user = current_user.get_id())
        db.session.add(new_note)
        db.session.commit()


    return render_template("home.html", user = current_user)
@views.route('/delete-note', methods = ['POST'])
def delete_note():
    note = json.loads(request.data)
    note_id = note['noteId']
    note = Note.query.get(note_id)
    print('got here')
    if note:
        if note.user == current_user.id:
            db.session.delete(note)
            db.session.commit()
    return jsonify ({})