from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:launchcode@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y337keefret43sdg3sf'

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(10000))

    def __init__(self, title, body):
        self.title = title
        self.body = body

@app.route('/', methods=['POST','GET'])
def index():
    return redirect("/blog")

@app.route('/blog', methods=['POST','GET'])
def blog():
    blog_id = request.args.get('id')
    posts = Blog.query.all()
    if blog_id:
        post = Blog.query.filter_by(id=blog_id).first()
        return render_template('singlepost.html', title=post.title, body=post.body)
    return render_template('blog.html', posts=posts)

@app.route('/newpost', methods=['POST','GET'])

def newpost():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        title_error = False
        body_error = False
        if title == "":
            flash("Enter a blog title")
            title_error = True
        if body == "":
            flash("Enter blog content")
            body_error = True
        if not title_error and not body_error:
            newpost = Blog(title, body)
            db.session.add(newpost)
            db.session.commit()
            post_id = newpost.id
            post_url = '/blog?id=' + str(post_id)
            return redirect(post_url)
        else:
            return render_template('newpost.html', title=title, body=body)
    return render_template('newpost.html')

if __name__ == '__main__':
    app.run()

