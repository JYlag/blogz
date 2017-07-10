#Build-A-Blog Project
#Created by: Joe Ylagan
#Partner: Sigala Hernandez

from flask import Flask, redirect, render_template, session, request, flash
from flask_sqlalchemy import SQLAlchemy
import cgi

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True

db = SQLAlchemy(app)

app.secret_key = "Hello"

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), unique=True)
    body = db.Column(db.String(2000))
    deleted = db.Column(db.Boolean)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):

        self.title = title
        self.body = body
        self.deleted = False
        self.owner = owner

    def __repr__(self):
        return '<Blog %r>' % self.title

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):

        self.username = username
        self.password = password


    def __repr__(self):
        return '<User &r' % self.username

def input_is_valid(text):
    return len(text) >= 3 and len(text) <= 20

def verify_passwords(password,verify_pass):
    return password == verify_pass

def get_blog_posts():
    return Blog.query.filter_by(deleted=False).all()

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route("/logout")
def logout():
    del session['username']
    return redirect("/blog")

@app.route("/signup", methods=['POST','GET'])
def signup():

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        existing_user = User.query.filter_by(username=username).first()
        if not existing_user:

            if not input_is_valid(username):
                flash("Username does not meet requirements. Please enter a different user", "error")
            if not input_is_valid(password):
                flash("Password does not meet requirements. Please try again.", "error")
            if not verify_passwords(password,verify):
                flash("Passwords do not match. Please try again.", "error")

            if input_is_valid(username) and input_is_valid(password) and verify_passwords(password,verify):
                new_user = User(username, password)
                db.session.add(new_user)
                db.session.commit()
                session['username'] = username
                return redirect('/blog')
        else:
            flash("Username already exists! Enter a different username", "error")
            return redirect("/signup")
    

    return render_template("signup.html")

@app.route("/login", methods=['POST', 'GET'])
def login():

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username
            flash("Logged In!")
            return redirect("/blog")
        else:
            flash("Username doesnt not exist, or password is incorrect.", "error")
            return redirect("/login")

    return render_template("login.html")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/new-post", methods=['GET'])
def add_post():
    return render_template('new-post.html')

@app.route("/posted", methods=["POST"])
def post():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        owner = User.query.filter_by(username=session['username']).first()

        if len(title) == 0 and len(body) == 0:
            flash("You didn't include a title. Please enter a title.", "error")
            flash("You forgot to add a description!", "error")
            return redirect("/new-post")

        if len(title) == 0:
            flash("You didn't include a title. Please enter a title.", "error")
            return redirect("/new-post")

        if len(body) == 0:
            flash("You forgot to add a description!", "error")
            return redirect("/new-post")

        blog_post = Blog(title=title, body=body, owner=owner)
        db.session.add(blog_post)
        db.session.commit()
        blog_post_id = str(blog_post.id)

        return redirect("/blog?id=" + blog_post_id)

@app.route("/blog", methods=['GET'])
def blog():

    post_id = request.args.get("id")
    if request.args.get("id") == None:
        return redirect("/blog?id=None")

    current_post = Blog.query.get(post_id)

    return render_template("blog.html", title="Blog Page", blog_post=get_blog_posts(), current_post=current_post)

if __name__ == "__main__":
    app.run()