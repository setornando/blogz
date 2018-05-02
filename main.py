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
    title = db.Column(db.Text)
    post = db.Column(db.Text)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, post, owner):
        self.title = title
        self.post = post
        self.owner = owner
    
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__ (self, username, password):
        self.username = username
        self.password = password

@app.before_request
def login_required():
    allowed_routes = ['login', 'signup', '/', 'index']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/', methods=['POST', 'GET'])
def index():
    users = User.query.distinct()
    author_id = request.args.get('username')
    if author_id:
        return redirect('/blog')
    return render_template('index.html', usernames=users)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username = username).first()
        if user:
            if user.password == password:
                session['username'] = username
                flash('Logged in as ' + session['username'])
                return redirect('/blog')
            else:
                flash('Invalid password. Please enter again.')
        else:
            flash('Invalid username. Please enter again.')
    return render_template('login.html')

@app.route('/signup', methods=['POST', 'GET'])
#user enters valid name and password
#redirected to '/newpost' page with their username stored in a session
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        pw_confirmation = request.form['confirm_password']
#if invalid  password for username that is in databae, redirected to '/login'with error message that pw incorrect
        if password != pw_confirmation:
            flash('Passwords do not match')
            return redirect('/signup')
        if password == '' or len(password) < 3:
            flash('Invalid password')
            return redirect('/signup')
#if invalid username not in database, redirected to '/login' with error message that username doesn't exist
        existing_user = User.query.filter_by(username=username).first()
        if not existing_user:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/newpost')
        else:
            flash('Username already exists')
            return render_template('signup.html')
    return render_template('signup.html')


@app.route('/blog', methods=['POST','GET'])
def blog():
    post_id = request.args.get('id')
    author_id = request.args.get('owner_id')
    all_posts = Blog.query.all()
    if post_id:
        single_post = Blog.query.get(post_id)
        return render_template('singlepost.html', posts=single_post)
    elif author_id:
        posts_from_author = Blog.query.filter_by(owner_id=author_id).all()

        return render_template('singleUser.html', posts=posts_from_author)
    
    return render_template('blog.html', posts=all_posts)

   
        
def is_empty(x):
    if len(x) == 0:
        return True
    else:
        return False


@app.route('/blogs')
def display_single_user():
    owner = request.args.get('user')
    user = User.query.filter_by(username=owner).first()
    blogs = Blog.query.filter_by(owner=user).all()
    return render_template('singleUser.html', blogs=blogs, user=user)

@app.route('/newpost')
def post():
    return render_template('newpost.html', title="New Blog Post")

@app.route('/newpost', methods=['POST','GET'])

def add_entry():
    if request.method == 'POST':
        title_error = ''
        blog_entry_error = ''

        post_title = request.form['blog_title']
        post_entry = request.form['blog_post']
        owner = User.query.filter_by(username=session['username']).first()
        new_post = Blog(post_title, post_entry, owner)

        if not is_empty(post_title) and not is_empty(post_entry):
            db.session.add(new_post)
            db.session.commit()
            post_link = "/blog?id=" + str(new_post.id)
            return redirect(post_link)
        else:
            if is_empty(post_title) and is_empty(post_entry):
                title_error = "Blog title is missing"
                blog_entry_error = "Blog content is missing"
                return render_template('newpost.html', title_error=title_error, blog_entry_error=blog_entry_error)
            elif is_empty(post_title) and not is_empty(post_entry):
                title_error = "Blog title is missing"
                return render_template('newpost.html', title_error=title_error, post_entry=post_entry)
            elif is_empty(post_entry) and not is_empty(post_title):
                blog_entry_error = "Blog content is missing"
                return render_template('newpost.html', blog_entry_error=blog_entry_error, post_title=post_title)

    else: 
        return render_template('newpost.html')

@app.route('/logout')
def logout():
    del session['username']
    flash('User logged out')
    return redirect('/')

if __name__ == '__main__':
    app.run()

