from flask import Flask,render_template,request,redirect,session,url_for,send_from_directory
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_
from datetime import datetime,timedelta
from werkzeug.security import check_password_hash,generate_password_hash
from werkzeug.utils import secure_filename
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

class Drive(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    company_id=db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)
    job_title=db.Column(db.String(200),nullable=False)
    job_description=db.Column(db.String(200))
    eligibility=db.Column(db.String(200))
    application_deadline=db.Column(db.Date)
    status=db.Column(db.String(20),default='pending')

    company=db.relationship('User')
    application=db.relationship('Application',backref='drive',cascade='all,delete-orphan')

class Application(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    student_id=db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)
    drive_id=db.Column(db.Integer,db.ForeignKey('drive.id'),nullable=False)
    application_date=db.Column(db.DateTime,default=datetime.now)
    status=db.Column(db.String(20),default='Applied')

    student=db.relationship('User')


# admin
def create_admin():
    if not User.query.filter_by(role='admin').first():
        admin=User(name='Admin',email='admin@gmail.com',role='admin',approval_status='approved')
        admin.set_password('1234')
        db.session.add(admin)
        db.session.commit()
        print('Admin created,admin@gmail.com,1234')

def logged_in():
    if 'user_id' in session:
        return User.query.get(session['user_id'])
    return None


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
            return redirect(url_for('admin_dashboard'))
        elif user.role=='company':
            return redirect(url_for('company_dashboard'))
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

@app.route("/admin_dashboard",methods=['GET','POST'])
def admin_dashboard():
    if session.get('role')!="admin":
        return render_template('index.html')
    total_student=User.query.filter_by(role="student").count()
    total_company=User.query.filter_by(role="company").count()
    total_place=Drive.query.count()
    total_app=Application.query.count()


    pending_comp=User.query.filter_by(role="company",approval_status='pending').all()
    all_students=User.query.filter_by(role="student").all()
    all_companies=User.query.filter_by(role="company").all()
    all_drives=User.query.filter_by(role="company").all()

    search_query=request.args.get('q','').strip()
    search_results_stud=[]
    search_results_comp=[]
    if search_query:
        like=f'%{search_query}%'
        search_results_stud=User.query.filter(
            User.role=='student',
            or_(User.name.like(like), User.email.like(like))).all()
        search_results_comp=User.query.filter(
            User.role=='company',
            or_(User.name.like(like), User.company_name.like(like))).all()


    return render_template('admin_dash.html'
                           ,total_students=total_student,
                           total_companies=total_company,
                           total_place=total_place,
                           total_app=total_app,

                           pending_comp=pending_comp,
                           all_students=all_students,
                           all_companies=all_companies,
                           all_drives=all_drives,
                           search_query=search_query,
                           search_results_stud=search_results_stud,
                           search_results_comp=search_results_comp
                           )

@app.route('/admin/approvecompany/<int:company_id>',methods=['GET','POST']) 
def approve_comp(company_id):
    if session.get('role')!='admin':
        return redirect(url_for('index'))
    company=User.query.get_or_404(company_id)
    company.approval_status='approved'
    # drive=Drive.query.filter_by(status='pending')
    # drive.status='approved'
    db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/rejectcompany/<int:company_id>',methods=['GET','POST']) 
def reject_comp(company_id):
    if session.get('role')!='admin':
        return redirect(url_for('index'))
    company=User.query.get_or_404(company_id)
    company.approval_status='rejected'
    # company.is_blacklisted='True'
    db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/studentblacklisted/<int:student_id>',methods=['GET','POST'])
def blacklists(student_id):
        if session.get('role')!='admin':
            return redirect(url_for('index'))
        student=User.query.get_or_404(student_id)
        student.is_blacklisted=not student.is_blacklisted

        db.session.commit()
        return redirect(url_for('admin_dashboard'))


# companydashboard
@app.route("/company_dashboard")
def company_dashboard():
    if session.get('role')!="company":
        return render_template('index.html')
    comp=logged_in()
    my_drives=Drive.query.filter_by(company_id=comp.id).all()
    applications={}
    for drive in my_drives:
        applications[drive.id]= Application.query.filter_by(drive_id=drive.id).all()
    return render_template('company_dash.html',
                           company=comp,
                           my_drives=my_drives,
                           applications=applications)

@app.route('/add_drive',methods=['GET','POST'])
def add_drive():
    if session.get('role')!="company":
        return render_template('index.html')
    comp=logged_in()
    if comp.approval_status !="approved":
        return redirect(url_for("company_dashboard"))
    job_title=request.form.get('job','').strip()
    print(job_title)
    job_description=request.form.get('job_desc','').strip()
    print(job_description)
    job_eligibility=request.form.get('job_eligibility','').strip()
    print(job_eligibility)
    deadline=request.form.get('deadline')
    drive=Drive(
        company_id=comp.id,
        job_title=job_title,
        job_description=job_description,
        eligibility=job_eligibility,
        application_deadline=datetime.strptime(deadline,'%Y-%m-%d').date() if deadline else None,
        status='approved'
    )
    print(drive)
    db.session.add(drive)
    db.session.commit()
    return redirect(url_for("company_dashboard"))

# @app.route('/company/drive/<int:drive_id>/edit',methods=['GET','POST'])
# def edit_drive(drive_id):
#     if session.get('role')!="company":
#         return render_template('index.html')
#     comp=logged_in()
#     drive=Drive.query.get_or_404(drive_id)
#     if drive.company_id != comp.id:
#         return redirect(url_for("index.html"))
#     drive.job_title=


@app.route('/company/drive/<int:drive_id>/close',methods=['GET','POST'])
def close_drive(drive_id):
    if session.get('role')!="company":
        return render_template('index.html')
    comp=logged_in()
    drive=Drive.query.get_or_404(drive_id)
    if drive.company_id != comp.id:
        return redirect(url_for("index.html"))
    drive.status='closed'
    db.session.commit()
    return redirect(url_for("company_dashboard"))

@app.route('/company/drive/<int:drive_id>/delete',methods=['GET','POST'])
def delete_drive(drive_id):
    if session.get('role')!="company":
        return render_template('index.html')
    comp=logged_in()
    drive=Drive.query.get_or_404(drive_id)
    if drive.company_id != comp.id:
        return redirect(url_for("index.html"))
    db.session.delete(drive)
    db.session.commit()
    return redirect(url_for("company_dashboard"))

@app.route('/company/drive/<int:application_id>/status',methods=['GET','POST'])
def update_application(application_id):
    if session.get('role')!="company":
        return render_template('index.html')
    comp=logged_in()
    application=Application.query.get_or_404(application_id)
    if application.drive.company_id !=comp.id:
        return redirect(url_for("index.html"))
    new_status=request.form.get('status')
    if new_status in ('Applied','selected','rejected','shortlisted'):
        application.status=new_status
        db.session.commit()
    return redirect(url_for("company_dashboard")) 



# student dashboard

@app.route("/student_dashboard")
def student_dashboard():
    if session.get('role')!="student":
        return render_template('index.html')
    stud=logged_in()
    approved_drives=Drive.query.filter_by(status='approved').all()
    applications=Application.query.filter_by(student_id=stud.id).all()
    applied_drive=[a.drive.id for a in applications]
    return render_template('student_dash.html',student=stud,
                           approved_drives=approved_drives,
                           applications=applications,
                           applied_drive=applied_drive)


@app.route('/student/drive/<int:drive_id>/apply',methods=['GET','POST'])
def apply_drive(drive_id):
    if session.get('role')!="student":
        return render_template('index.html')
    stud=logged_in()
    drive=Drive.query.get_or_404(drive_id)
    if drive.status!='approved':
        return redirect(url_for('student_dashboard'))
    exist=Application.query.filter_by(student_id=stud.id,drive_id=drive.id).first()
    if exist:
        return redirect(url_for('student_dashboard'))
    application=Application(student_id=stud.id,drive_id=drive.id,status='Applied') 
    db.session.add(application)
    db.session.commit()
    return redirect(url_for('student_dashboard'))


@app.route("/edit_profile",methods=['GET','POST'])
def edit_profile():
    if session.get('role')!='student':
        return redirect(url_for('index'))
    stud=logged_in()
    stud.name=request.form.get('name','').strip()
    stud.phone=request.form.get('phone','').strip()
    resume=request.files.get('resume')
    print(resume)
    if resume and resume.filename:
        print(resume.filename)
        filename=secure_filename(f"user_{stud.id}_{resume.filename}")
        filepath=os.path.join(app.config['UPLOAD_FOLDER'],filename)
        resume.save(filepath)
        stud.resume_path=filename
    db.session.commit()
    return redirect(url_for('student_dashboard'))

@app.route('/uploads/<filename>')
def uploded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)



# run the app

with app.app_context():
    db.create_all()
    create_admin()

if __name__=='__main__':
    app.run(debug=True)


   