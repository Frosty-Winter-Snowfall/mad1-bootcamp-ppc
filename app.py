from flask import Flask,render_template,request,redirect,session,url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime,timedelta
from werkzeug.security import check_password_hash,generate_password_hash
import os




app=Flask(__name__)
app.config['SECRET_KEY']="pass"
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///placement.db'
app.config['UPLOAD_FOLDER'] = os.path.join("static",'uploads')

db=SQLAlchemy(app)

# models

class User(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(100), nullable=False)
    email=db.Column(db.String(100), unique=True,nullable=False)
    password_hash=db.Column(db.String(200),nullable=False)
    role=db.Column(db.String(20), nullable=False)
    # resume_path=db.Column(db.String(300))
    # is_blacklisted=db.Column(db.Boolean,default='False')
    # created_at=db.Column(db.DateTime,default=datetime.now)

    def set_password(self,raw):
        self.password_hash=generate_password_hash(raw)
    def check_password(self,raw):
        return check_password_hash(self.password_hash, raw)



@app.route("/")
def index():
    return render_template('index.html')

@app.route("/login",methods=['GET','POST'])
def login():
    if request.method=="POST":
        email=request.form.get('email'," ").strip()
        password=request.form.get('password'," ")
        print(email)
        print(password)
        user=User.query.filter_by(email=email).first()
        if not email or not password:
            return render_template('index.html')
        if user.is_blacklisted:
            return render_template('index.html')
    return render_template("login.html")

@app.route("/signup",methods=['GET','POST'])
def signup():
    if request.method=='POST':
        role=request.form.get('role')
        print(role)
        name=request.form.get('name'," ").strip()
        print(name)
        email=request.form.get('email'," ").strip()
        print(email)
        password=request.form.get('password'," ")
        print(password)
        if not name or not email or not password or role not in ('student','company'):
            return render_template('index.html')
        exist=User.query.filter_by(email=email).first()
        if exist:
            return render_template("signup.html",error="Email already exists")
        user=User(name=name, email=email, role=role,)
        user.set_password(password)
        print(user)

        if role=='student':
            print("hi student")
        if role=='company':
            print("hi company")
        db.session.add(user)
        db.session.commit()
        return redirect("/")
    return render_template('signup.html')


with app.app_context():
    db.create_all()

if __name__=='__main__':
    app.run(debug=True)


   