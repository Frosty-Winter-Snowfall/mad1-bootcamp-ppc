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

    resume_path=db.Column(db.String(300))
    phone=db.Column(db.String(20))
    company_name=db.Column(db.String(200))
    hr_contact=db.Column(db.String(200))
    website=db.Column(db.String(200))
    approval_status=db.Column(db.String(20),default='pending')
    is_blacklisted=db.Column(db.Boolean,default=False)

    created_at=db.Column(db.DateTime,default=datetime.now)

    def set_password(self,raw):
        self.password_hash=generate_password_hash(raw)
    def check_password(self,raw):
        return check_password_hash(self.password_hash, raw)

# admin
def create_admin():
    if not User.query.filter_by(role='admin').first():
        admin=User(name='Admin',email='admin@gmail.com',role='admin',approval_status='approved')
        admin.set_password('1234')
        db.session.add(admin)
        db.session.commit()
        print('Admin created,admin@gmail.com,1234')



#login/signup/logout

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
            return render_template('login.html',error='Fill all fields')
        if not user or not user.check_password(password):
            return render_template('login.html',error='Your password is wrong')
        if user.role=='company' and user.approval_status!='approved':
            return render_template('login.html',error='Your account is pending approval')
        if user.is_blacklisted:
            return render_template('login.html',error='Your account is blacklisted')
        session['user_id']=user.id
        session['role']=user.role
        session['name']=user.name
        if user.role=='admin':
            return redirect(url_for('admin_dash'))
        elif user.role=='company':
            return redirect(url_for('company_dash'))
        else:
            return redirect(url_for('student_dashboard'))

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
            user.phone=request.form.get('number')

        if role=='company':
            # print("hi company")
            user.company_name=request.form.get('company_name',' ').strip()
            user.hr_contact=request.form.get('hr_contact',' ').strip()
            user.website=request.form.get('website',' ').strip()

        db.session.add(user)
        db.session.commit()
        return redirect("/")
    return render_template('signup.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))



# admin dashboard

@app.route("/admin_dashboard")
def admin_dashboard():
    return render_template('admin_dash.html')




# company dashboard
@app.route("/company_dashboard")
def company_dashboard():
    return render_template('company_dash.html')



# student dashboard

@app.route("/student_dashboard")
def student_dashboard():
    return render_template('student_dash.html')







# run the app

with app.app_context():
    db.create_all()
    create_admin()

if __name__=='__main__':
    app.run(debug=True)


   