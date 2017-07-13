#Build-A-Blog Project
#Created by: Joe Ylagan
#Partner: Sigala Hernandez

from flask import redirect, render_template, session, request, flash
from app import app, db
from models import User, Blog
from hashutils import make_salt, make_pw_hash, check_pw_hash

app.secret_key = "Hello"

def input_is_valid(text):
    return len(text) >= 3 and len(text) <= 20

def verify_passwords(password,verify_pass):
    return password == verify_pass

def get_blog_posts():
    return Blog.query.filter_by(deleted=False).all()

def get_user_posts(username):
    
    user = User.query.filter_by(username=username).first()

    return Blog.query.filter_by(owner_id=user.id).all()

def get_users():
    return User.query.all()

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'index']
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
                return redirect('/new-post')
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
        if user and check_pw_hash(password, user.pw_hash):
            session['username'] = username
            flash("Logged In!")
            return redirect("/blog")
        else:
            flash("Username doesnt not exist, or password is incorrect.", "error")
            return redirect("/login")

    return render_template("login.html")

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

    user = request.args.get('user')
    if not user:
        post_id = request.args.get("id")
        if not post_id:
            return redirect("/blog?id=All")
        current_post = Blog.query.get(post_id)
        return render_template("blog.html", title="Blog Page",blog_post=get_blog_posts(),current_post=current_post)
    
    if get_user_posts(user):
        user_posts = get_user_posts(user)
    else:
        user_posts = "No posts yet"

    return render_template("blog.html", title="Blog Page",blog_post=get_blog_posts(), user_posts=user_posts)

@app.route("/", methods=['GET'])
def index():
    author = request.args.get("user")

    return render_template("index.html", userlist=get_users())

if __name__ == "__main__":
    app.run()