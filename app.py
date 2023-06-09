from flask import Flask, render_template, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditor, CKEditorField

import requests
import datetime


## Delete this code:
# import requests
# posts = requests.get("https://api.npoint.io/43644ec4f0013682fc0d").json()

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
ckeditor = CKEditor(app)
Bootstrap(app)

##CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

##CONFIGURE TABLE
class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(250), nullable=False)
    img_url = db.Column(db.String(250), nullable=False)


##WTForm
class CreatePostForm(FlaskForm):
    title = StringField("Blog Post Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    author = StringField("Your Name", validators=[DataRequired()])
    img_url = StringField("Blog Image URL", validators=[DataRequired(), URL()])
    body = CKEditorField("Blog Content", validators=[DataRequired()])
    submit = SubmitField("Submit Post")
    


@app.route('/')
def get_all_posts():
    posts = BlogPost.query.all()
    return render_template("index.html", all_posts=posts)


@app.route("/post/<int:post_id>")
def show_post(post_id):
    requested_post = BlogPost.query.get(post_id)
    return render_template('post.html',ckeditor=ckeditor ,post = requested_post)

@app.route('/new-post',methods=['GET','POST'])
def create_new_post():
    form = CreatePostForm()
    title = 'Create a new post'
    if form.validate_on_submit():
        new_post = BlogPost(
            title = form.title.data,
            subtitle = form.subtitle.data,
            body = form.body.data,
            img_url = form.img_url.data,
            author = form.author.data,
            date = datetime.date.today().strftime("%B %d, %Y")
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for('get_all_posts'))

    return render_template('make-post.html',form=form,title_temp=title)




@app.route("/edit-post/<int:post_id>",methods=['GET','POST'])
def edit_post(post_id):
    thepost= BlogPost.query.get(post_id)
    editform = CreatePostForm(
        title = thepost.title,
        subtitle = thepost.subtitle,
        author = thepost.author,
        img_url = thepost.img_url,
        body = thepost.body
    )
    if editform.validate_on_submit():
        
        thepost.title = editform.title.data
        thepost.subtitle = editform.subtitle.data
        thepost.img_url = editform.img_url.data
        thepost.author = editform.author.data
        thepost.body = editform.body.data
        
        db.session.commit()
        
        return redirect(url_for('show_post',post_id = thepost.id))
    title = 'Edit Post'
    
    return render_template('make-post.html',form=editform,title_temp=title)


@app.route('/delete/<int:post_id>')
def delete_post(post_id):
    post_to_delete = BlogPost.query.get(post_id)
    db.session.delete(post_to_delete)
    db.session.commit()

    posts = BlogPost.query.all()
    return render_template('index.html',all_posts = posts)
    #get_all_posts

@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")

if __name__ == "__main__":
    app.run(debug=True,host='0.0.0.0', port=5000)