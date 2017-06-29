#Build-A-Blog Project
#Created by: Joe Ylagan
#Partner: Sigala Hernandez

from flask import Flask, redirect, render_template, session, request, flash
from flask_sqlalchemy import SQLAlchemy
import cgi

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:build-a-blog@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True

db = SQLAlchemy(app)

app.secret_key = "Hello"

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), unique=True)
    body = db.Column(db.String(2000))
    deleted = db.Column(db.Boolean)

    def __init__(self, title, body):

        self.title = title
        self.body = body
        self.deleted = False

    def __repr__(self):
        return '<Blog %r>' % self.title

def get_blog_posts():
    return Blog.query.filter_by(deleted=False).all()

@app.route("/new-post", methods=['GET'])
def add_post():
    return render_template('new-post.html')

@app.route("/posted", methods=["POST"])
def post():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']

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

        blog_post = Blog(title=title, body=body)
        db.session.add(blog_post)
        db.session.commit()
        blog_post_id = str(blog_post.id)

        return redirect("/blog?id=" + blog_post_id)

@app.route("/blog", methods=['GET'])
def index():

    post_id = request.args.get("id")
    if request.args.get("id") == None:
        return redirect("/blog?id=None")

    current_post = Blog.query.get(post_id)

    return render_template("blog.html", title="Blog Page", blog_post=get_blog_posts(), current_post=current_post)

if __name__ == "__main__":
    app.run()