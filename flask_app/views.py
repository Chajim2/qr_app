from flask import Blueprint, redirect, render_template, request, jsonify, url_for, flash
from .models import Note, User, Img, create_secret_key
from. import db
from flask_login import login_required, current_user
from sqlalchemy.sql import func
import json, PIL.Image as Image, qrcode
from PIL import Image


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

@views.route('/profile',methods=['POST','GET'])
@login_required
def profile():
    return render_template('profile.html', user = current_user, path = f"{current_user.id}.png")

@views.route('/upload/<id>', methods = ["POST", "GET"])
def upload_file(id): 
    #gets data from form from profile.html
    pic = request.files['pic']
    #checks if data is viable
    try:
        curr_img = Image.open(pic)
    except:
        flash(f"something wrong with image", category="error")
        return redirect(url_for("views.profile"))
    
    if not check_img(curr_img): 
        flash(f"wrong IMAGE FORMAT  {curr_img.format}", category="error")
        return redirect(url_for('views.profile'))

    # saves into outside file (could use cloud here)
    curr_img.save(f'flask_app/static/{id}.png')

    # adds to db
    suff = curr_img.format
    img = Img(mimetype = suff, user = id)
    db.session.add(img)
    db.session.commit()

    flash("IMAGE CHANGED", category="succes")
    return redirect(url_for('views.profile'))

@views.route('/delete-note', methods = ['POST'])
def delete_note():
    #idfk what this does ngl
    note = json.loads(request.data)
    note_id = note['noteId']
    note = Note.query.get(note_id)
    if note:
        if note.user == current_user.id:
            db.session.delete(note)
            db.session.commit()
    return jsonify ({})


@views.route('/friends',methods = ["POST","GET"])
@login_required
def friends():
    alerts = listify(current_user.alerts)
    alerts = set(alerts)
    friends = listify(current_user.friends)
    return render_template("friends.html", user = current_user, alerts = list(alerts), friends = friends)

@views.route('/remove_alert_accept/<fname>', methods =["POST"])
@login_required
def remove_alert_accept(fname):
    #removes user from alerts
    deleted_user = User.query.filter_by(fname = fname).first() 
    alert_list = current_user.alerts.split(",")
    print (f"list is:{current_user.alerts} x is:{deleted_user.fname}, current_user is {current_user.fname}")
    alert_list.remove(deleted_user.fname)
    current_user.alerts = ",".join(alert_list)
    db.session.commit()
    #adds them to friendlist
    if current_user.friends == None: friend_list = []
    else: friend_list = current_user.friends.split(",")
    friend_list.append(deleted_user.fname)
    current_user.friends = ",".join(friend_list)
    db.session.commit()
    return redirect("/friends")

@views.route('/remove_alert_decline/<fname>', methods =["POST"])
@login_required
def remove_alert_decline(fname):
    #removes user from alerts
    deleted_user = User.query.filter_by(fname = fname).first() 
    alert_list = current_user.alerts.split(",")
    print (f"list is:{current_user.alerts} x is:{deleted_user.fname}, current_user is {current_user.fname}")
    alert_list.remove(deleted_user.fname)
    current_user.alerts = ",".join(alert_list)
    db.session.commit()
    return redirect("/friends")

@views.route('/add_friend', methods=["POST"])
def add_friend():
    # takes the name of the person u are sending to (NOT THE ONE BEING SENT TO!!!)
    fname_sent = request.form['name']
    target_user = User.query.filter_by(fname = fname_sent).first()
    # this works : flash(user.lname, category="error")
    if not target_user: 
        flash("user doesnt exist", category="error")
    elif str(target_user.fname) == str(current_user.fname): flash("can't add urself", category="error")
    #adding the alert to the one being sent to, NOT THE ONE SENDING
    else:
        target_user.alerts = str(target_user.alerts) + ',' +  str(current_user.fname)
        db.session.commit()
        flash(f"added {target_user.fname} sucesfully", category="succes")
    return redirect("/friends")

@views.route('/qr_code', methods=["POST","GET"])
@login_required
def qr_code():
    user_qr = qrcode.make(f"http://127.0.0.1:5000/qr_add_friend-{current_user.fname}-{current_user.secret_key}")  
    user_qr.save("flask_app/static/temp.png")
    return render_template("qr.html", user = current_user)

@views.route('/qr_add_friend-<friend>-<key>')
@login_required
def qr_add_friend(friend, key):
    #friend is the one who is being scanned, current user is scaning
    friend = User.query.filter_by(fname = friend).first()
    if key != friend.secret_key:
        flash("wrong qr code or link", category="error")
        return redirect("/friends")
    elif current_user.fname == friend:
        flash("cant add yourself",category="error")
        return redirect("/friends")
    
    friend.secret_key = create_secret_key()
    #add friend into current users friends
    curr_friends_string = listify(current_user.friends)
    curr_friends_string.append(friend.fname)
    current_user.friends = stringify(curr_friends_string)
    db.session.commit()

    #add current user into friends friends
    friend_friends_string = listify(friend.friends)
    friend_friends_string.append(current_user.fname)
    friend.friends = stringify(friend_friends_string)
    db.session.commit()


    flash(f"added {current_user.fname} into {friend.fname}s friends and vice versa")
    return redirect("/friends")
    

def stringify(lst) -> str:
    if lst is None: return ""
    if len(lst) == 0: return ""
    elif len(lst) == 1: return lst[0]
    else: return ",".join(lst)

def listify(strg) -> list:
    if strg is None: return []
    elif len(strg) == 0: return []
    elif ',' not in strg: return [strg]
    else: 
        out = strg.split(',')
        if "" in out: out.remove("")
        return out
    

def check_img(curr_img):
    # get image format and check it
    suff = curr_img.format
    if suff.lower() not in ("png","jpg","jpeg"):
        return False
    return suff