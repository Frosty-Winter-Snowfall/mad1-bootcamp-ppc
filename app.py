from flask import Flask,render_template,request
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash,generate_password_hash


app=Flask(__name__)
app.config['SECRET_KEY']="pass"
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///placement.db'

db=SQLAlchemy(app)


class User(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    email=db.Column(db.String(100), nullable=False)
    password=db.Column(db.String(200),nullable=False)



@app.route("/")
def index():
    return render_template('index.html')

@app.route("/login",methods=['GET','POST'])
def login():
    if request.method=="POST":
        email=request.form.get("em")
        password=request.form.get("pass")
        print(email)
        print(password)
    return render_template("login.html")

# @app.route("/signup")
# def signup():

    # return render_template(signup.html
    #                        )


with app.app_context():
    db.create_all()

if __name__=='__main__':
    app.run(debug=True)


    # 40 total
    # 3X2=6 theory questions
    # 3 flow
    # 2 coding quetsions 2X2=4

    # 13

    # 40=13(coding and theory_)+27(functionalities)   