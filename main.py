from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:launchcode@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y337keefret43sdg3sf'

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(10000))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, user):
        self.title = title
        self.body = body
        self.user = user
    
    def __repr__(self):
        return '<Blog %r>' % self.title
    
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='user')

    def __init__ (self, username, password):
        self.username = username
        self.password = password


@app.before_request
def login_required():
    allowed_routes = ['login', 'signup', '/']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/', methods=['POST','GET'])
def get_logged_in_user():
    username = User.query.all()
    return render_template('index.html', username=username)

#def get_logged_in_user():
    #return User.query.filter_by(user=session['user']).first()

#def get_current_blogs(logged_in_user):
    #return Blog.query.filter_by(posts=True).all()



@app.route('/blog', methods=['POST','GET'])
def blog():
    if request.method == 'GET':
        posts = Blog.query.all()
        return render_template('blog.html', posts=posts)
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
        user = request.form['user']
        title_error = False
        body_error = False
        if title == "":
            flash("Enter a blog title")
            title_error = True
        if body == "":
            flash("Enter blog content")
            body_error = True
        if not title_error and not body_error:
            newpost = Blog(title, body, user)
            db.session.add(newpost)
            db.session.commit()
            post_id = newpost.id
            post_url = '/blog?id=' + str(post_id)
            return redirect(post_url)
        else:
            return render_template('newpost.html', title=title, body=body)
    return render_template('newpost.html')

@app.route('/signup', methods=['POST', 'GET'])
#user enters valid name and password
#redirected to '/newpost' page with their username stored in a session
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        pw_confirmation = ['confirm_password']
#if invalid  password for username that is in databae, redirected to '/login'with error message that pw incorrect
        if password != pw_confirmation:
            flash('Passwords do not match')
            return redirect('/signup')
        if password == '' or len(password) < 3:
            flash('Invalid password')
            return redirect('/signup')
        existing_user = User.query.filter_by(username=username).first()
        if not existing_user:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('newpost')
        else:
            flash('Username already exists')
    return render_template('signup.html')
        

#if invalid username not in database, redirected to '/login' with error message that username doesn't exist


@app.route('/login')
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username = username).first()
        if user:
            if user.password == password:
                session['username'] = username
                flash('Logged in as' + session['username'])
                return redirect('/blog')
            else:
                flash('Invalid password. Please enter again.')
        else:
            flash('Invalid username. Please enter again.')
    return render_template('login.html')


#@app.route('/index')

#@app.route('/logout', 'POST')
#def logout():
    #escape username from session
    #return redirect('/blog')

if __name__ == '__main__':
    app.run()

