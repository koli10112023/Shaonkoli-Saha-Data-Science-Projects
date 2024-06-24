import os
from datetime import datetime
from matplotlib import pyplot as plt
import sqlite3 as con
from flask import Flask
from flask import render_template
from flask import request, abort, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import insert
import tkinter as tk
current_dir=os.path.abspath(os.path.dirname(__file__))

app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']="sqlite:///"+os.path.join(current_dir,"trackerDB.sqlite3")
db=SQLAlchemy()
db.init_app(app)
app.app_context().push()

class User(db.Model):
    __tablename__ = 'user'
    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    username=db.Column(db.String, nullable=False)
    password=db.Column(db.String, nullable=False)
    
class Tracker(db.Model):
    __tablename__ = 'tracker'
    id = db.Column(db.Integer, autoincrement=True,primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)
    description=db.Column(db.String)
    ttype=db.Column(db.String, nullable=False)
    settings=db.Column(db.String)
    userid=db.Column(db.Integer, db.ForeignKey("user.user_id"),nullable=False)
    log_time=db.Column(db.String)

class Logger(db.Model):
    __tablename__ = 'Logger'
    user_id = db.Column(db.Integer, nullable=False)
    tracker_id = db.Column(db.Integer,db.ForeignKey("tracker.id"),nullable=False)
    track_time=db.Column(db.String, nullable=False)
    value=db.Column(db.String)
    note=db.Column(db.String)
    logger_id=db.Column(db.Integer, autoincrement=True,primary_key=True)


@app.route("/",methods=["GET","POST"])
def log():
    if request.method == "POST":
        user = request.form["username"]
        passw = request.form["password"]
        user_det = db.session.query(User).filter(User.username == user).all()
        if not user_det:
            conn = con.connect("trackerDB.sqlite3")
            conn.execute("INSERT INTO user (username,password) values (?,?)",(user,passw))
            conn.commit()
        else:
            msg = "Try some different username!!!"
            title = "User already exist!!!"
            popupmsg(msg, title)
                            
    return render_template('logging.html')    

@app.route("/dashboard",methods=["GET","POST"])
def logging():
    if request.method == "POST":
        user = request.form["username"]
        passw = request.form["password"]
        user_det = User.query.all()
        
        tracker=Tracker.query.all()
        if not user_det:
            return render_template("no_user.html")
        else:
            flag = False
            for use in user_det:
                if use.username == user:
                    flag = True
                    tracker=db.session.query(Tracker).join(User).filter(Tracker.userid == use.user_id).all()
                    uid = use.user_id
                    if not tracker:
                        return render_template("index.html",username=user)
                    else:
                        if use.password == passw:
                            return render_template("dashboard.html",track=tracker,username=user)
                        else:
                            msg = "Invalid username/password. Please try again!!!"
                            title = "Wrong credentials!!!"
                            popupmsg(msg, title)
                            return redirect(url_for('log')) 
            if not flag:
                return render_template("no_user.html")
    else:
        return redirect(url_for('log'))
        
@app.route("/dashboard/tracker/<user>",methods=["GET","POST"])        
def home(user):     
    uid = db.session.query(User).filter(User.username == user).all()
    for i in uid:
        tracker=db.session.query(Tracker).join(User).filter(Tracker.userid == i.user_id).all()
        if not tracker:
            return render_template("index.html",username=user)
        else:
            return render_template("dashboard.html",track=tracker,username=user)
        
@app.route("/dashboard/user",methods=["GET","POST"])
def add_user():
    return render_template("register_user.html")
    
@app.route("/dashboard/create/<user>",methods=["GET","POST"])
def add_tracker(user):
    if request.method == "GET":
        return render_template("add_tracker.html",username=user)
    elif request.method == "POST":
        name = request.form["t_name"]
        desc = request.form["desc1"]
        ttype = request.form["Type"]
        sett = request.form["s_name"]
        user_det = db.session.query(User).filter(User.username == user).all()
        for u in user_det:
            tracker=db.session.query(Tracker).join(User).filter(Tracker.name == name,Tracker.userid == u.user_id).all()
            if not tracker:
                for i in user_det:
                    add_rec(name,desc,ttype,sett,i.user_id)
                    return redirect(url_for('home',user=i.username))
            else:
                return render_template("tracker_exist.html",username=user)
            
def add_rec(name,desc,ttype,sett,uid):
    conn = con.connect("trackerDB.sqlite3")
    dt = datetime.now()
    now = dt.strftime("%d/%m/%Y %H:%M:%S")
    conn.execute("INSERT INTO tracker (name,description,ttype,settings,userid,log_time) values (?,?,?,?,?,?)",(name,desc,ttype,sett,uid,now))
    conn.commit()


@app.route("/dashboard/<user>/<int:id>/update_tracker",methods=["GET","POST"])
def tracker_update(id,user):
    if request.method == "POST":
        up_tracker(id)
        return redirect(url_for('home',user=user))
    else:
        return render_template("update_tracker.html",vid=id,username=user)
        
def up_tracker(id):
    name = request.form["t_name"]
    desc = request.form["desc1"]
    ttype = request.form["Type"]
    sett = request.form["s_name"]
        
    tracker=db.session.query(Tracker).filter(Tracker.name == name).all()
    conn = con.connect("trackerDB.sqlite3")
    dt = datetime.now()
    now = dt.strftime("%d/%m/%Y %H:%M:%S")
    conn.execute("UPDATE tracker set name=?,description=?,ttype=?,settings=?,log_time=? WHERE id=?",(name,desc,ttype,sett,now,id))
    conn.commit()

@app.route("/dashboard/<user>/<int:id>/delete_tracker", methods=["GET","POST"])     
def del_tracker(id,user):
    conn = con.connect("trackerDB.sqlite3")
    conn.execute("DELETE FROM logger where tracker_id = ?",(id,))
    conn.execute("DELETE FROM tracker where id = ?",(id,))
    conn.commit()
    return redirect(url_for('home',user=user))

@app.route("/dashboard/<user>/<int:id>", methods=["GET","POST"])     
def tracker_details(id,user):        
    logger = db.session.query(Logger).join(Tracker).filter(Tracker.id == id).order_by(Logger.track_time).all()
    tracker=db.session.query(Tracker).filter(Tracker.id == id).all()
    tracker_graph(logger,tracker)
    if not logger:
        return render_template("log_index.html",vid=id,username=user)
    else:
        return render_template("show_tracker.html",log=logger,username=user,vid=id)

def tracker_graph(logger,tracker):
    x = []
    y = []
    for i in logger:
        x.append(i.track_time)
        if i.value.isdigit():
            y.append(float(i.value))
        elif i.value.lower() in ['true','false']:
            if i.value.lower() == 'true':
                y.append(1)
            else:
                y.append(0)
        else:
            for j in tracker:
                if i.value.lower() in j.settings.lower():
                    if i.value.lower() == "angry":
                        y.append(0)
                    elif i.value.lower() == "sad":
                        y.append(1)
                    elif i.value.lower() == "meh":
                        y.append(2)
                    elif i.value.lower() == "okay":
                        y.append(3)
                    elif i.value.lower() == "calm":
                        y.append(4)
                    elif i.value.lower() == "happy":
                        y.append(5)
                    elif i.value.lower() == "very happy":
                        y.append(6)
    
    fig,ax = plt.subplots(figsize =(10, 7))
    plt.plot(x,y)
    plt.xlabel('Timestamp')
    plt.ylabel('Value')
    fig.savefig('static/my_plot.png')
    
                
    
@app.route("/dashboard/<user>/<int:id>/add_log",methods=["GET","POST"])    
def add_log(id,user):
    if request.method == "POST":
        time = request.form["time"]
        val = request.form["val"]
        desc = request.form["note"]
        
        add_log(id,time,val,desc,user)
        return redirect(url_for('home',user=user))
        
    return render_template("add_log.html",vid=id,username=user)

def add_log(id,time,val,desc,user):
    conn = con.connect("trackerDB.sqlite3")
    try:
        ttime = datetime.strptime(time, '%d-%m-%Y %H:%M:%S')
        success = 1
    except:
        msg = "Enter proper time in dd-mm-yyyy hh24:mi:ss format"
        title = "Wrong!!!"
        success = 0
        popupmsg(msg, title)
    if success == 1:
        tracker = db.session.query(Tracker).filter(Tracker.id == id).all()
        msg = ''  
        print(val)
        for i in tracker:
            if i.ttype.lower() == "type1":
                if not val.isdigit():
                    flag = False
                else:
                    flag = True
                    val=val*2
            elif i.ttype.lower() == "type2":
                sett = i.settings.split(',')
                for b in range(len(sett)):
                    sett[b]=sett[b].lower().strip()
                print(sett)
                if not val.isdigit():
                    print(val)
                    if val.lower() in sett:
                        print(val)
                        flag = True
                        break
                    else:
                        msg = 'Your value should be within '+i.settings
                        flag = False
                else:
                    flag = False
            elif i.ttype.lower() == "type3":   
                if not val.isdigit():
                    flag = False
                else:
                    flag = True
            elif i.ttype.lower() == "type4":
                if not val.isdigit():
                    if val.lower() in ['true','false']:
                        flag = True
                    else:
                        flag = False
                else:
                    flag = False
            else:
                flag = False
        if flag:    
            uid = db.session.query(User).filter(User.username == user).all()
            for i in uid:
                conn.execute("INSERT INTO logger(user_id,tracker_id,track_time,value,note) VALUES (?,?,?,?,?)",(i.user_id,id,ttime,val,desc))
                dt = datetime.now()
                now = dt.strftime("%d/%m/%Y %H:%M:%S")
                conn.execute("UPDATE tracker set log_time = ? WHERE id = ? and userid = ?",(now,id,i.user_id))
            conn.commit()
        else:
            if msg == '':
                msg = "Invalid Input!!!"
            title = "Wrong!!!"
            popupmsg(msg, title)

@app.route("/dashboard/<user>/<int:id>/<int:logger_id>/update_log",methods=["GET","POST"])    
def log_update(id,logger_id,user):
    use = db.session.query(User).filter(User.username==user).all()
    for i in use:
        uid = i.user_id
    if request.method == "POST":
        up_log(id,logger_id,uid)
        return redirect(url_for('tracker_details',id=id,user=user))
    else:
        return render_template("update_log.html",vid=id,lid=logger_id,username=user)
        
def up_log(id,logger_id,uid): 
    time = request.form["time"]
    val = request.form["val"]
    desc = request.form["note"]
    
    logger = db.session.query(Logger).join(Tracker).filter(Tracker.id == id).all()
    conn = con.connect("trackerDB.sqlite3")
    ttime = datetime.strptime(time, '%d-%m-%Y %H:%M:%S')
    conn.execute("UPDATE logger set track_time = ?, value = ?, note = ? WHERE tracker_id = ? and logger_id = ?",(ttime,val,desc,id,logger_id))
    dt = datetime.now()
    now = dt.strftime("%d/%m/%Y %H:%M:%S")
    conn.execute("UPDATE tracker set log_time = ? WHERE id = ? and userid = ?",(now,id,uid))
    conn.commit()

@app.route("/dashboard/<user>/<int:id>/<int:logger_id>/delete_log",methods=["GET","POST"])    
def log_delete(id,logger_id,user):
    conn = con.connect("trackerDB.sqlite3")
    conn.execute("DELETE FROM logger where tracker_id = ? and logger_id = ?",(id,logger_id,))
    conn.commit()
    return redirect(url_for('tracker_details',id=id,user=user))

def popupmsg(msg, title):
    root = tk.Tk()
    root.title(title)
    root.geometry('500x300')
    label = tk.Label(root, text=msg)
    label.pack(side="bottom", fill="x", pady=10)
    B1 = tk.Button(root, text="Okay", command = root.destroy)
    B1.pack()
    root.mainloop()
    
if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        debug=True,
        port=8080
    )