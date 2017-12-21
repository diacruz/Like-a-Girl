from flask import Flask, render_template, session, url_for, redirect, request, flash
from passlib.hash import sha256_crypt
from functools import wraps
from flask_pymongo import PyMongo

# Models
from models.user_model import LoginForm, RegisterForm, Feed

app = Flask(__name__)

# DB
app.config['MONGO_DBNAME'] = 'advising'
app.config['MONGO_URI'] = 'mongodb://admin:admin@ds121464.mlab.com:21464/likeagirl'
mongo = PyMongo(app)

# Decorator to check if logged in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'is_logged_in' in session:
            return f(*args, **kwargs)
        flash('Unauthorized, please login', 'danger')
        return redirect(url_for('index'))
    return wrap

# Home route
@app.route('/', methods = ['POST', 'GET'])
def index():
    session.clear()    
    form = LoginForm(request.form)
    return render_template('index.html', form = form)


# Login route
@app.route('/login', methods = ['POST', 'GET'])
def login():    
    form =  LoginForm(request.form)
    session.pop('is_logged_in', None)
    if request.method == 'POST' and form.validate():
        users = mongo.db.users
        login_user = users.find_one({'email': request.form['email']})
        if login_user:
            password = login_user['password']
            password_candidate = request.form['password']
            if sha256_crypt.verify(password_candidate, password):
                session['email'] = request.form['email']
                session['firstname'] = login_user['firstname']
                session['lastname'] = login_user['lastname']
                session['username'] = login_user['firstname']
                session['id'] = str(login_user['_id'])
                session['is_logged_in'] = True
            return redirect(url_for('feed'))    
        flash('Invalid password or email combination', 'danger')
    return render_template('index.html', form = form)

# Register Router
@app.route('/register', methods = [ 'POST', 'GET'])
def register():
    form = RegisterForm(request.form)
    users = mongo.db.users
    if request.method == 'POST' and form.validate():
        existing_user = users.find_one({'email': request.form['email']})
        if not existing_user:
            hashpass = sha256_crypt.encrypt(str(form.password.data))
            users.insert({
                          'email': request.form['email'],
                          'firstname': request.form['firstname'],
                          'lastname': request.form['lastname'],
                          'pic':'https://cdn.pixabay.com/photo/2014/04/03/10/32/user-310807_960_720.png',
                          'password': hashpass})
            flash('You are now registered and can log in', 'success')
            return redirect(url_for('index', form=form))
        flash('Email already exists', 'danger')
    return render_template('register.html', form = form)

# FEED
@app.route('/feed', methods = ['POST' , 'GET'])
@is_logged_in
def feed():
    form = Feed(request.form)
    posts = mongo.db.posts
    if request.method == 'POST' and form.validate():
        new_post = {
            'title' : request.form['title'],
            # 'image' : request.form['image'],
            'author' : session['firstname'],
            'body' : request.form['body'],
            'likes' : 0
        }
        posts.insert(new_post)
    post_list = reversed(list(posts.find({})))
    return render_template('feed.html', form=form, posts=post_list, users = mongo.db.users)


    return render_template('feed.html')


# Profile
@app.route('/profile', methods = ['GET', 'POST'])
@is_logged_in
def redir_profile():
    return profile(session['firstname'])

# Profile by ID 
@app.route('/profile/<string:username>', methods = ['GET', 'POST'])
@is_logged_in
def profile(username):
    posts = mongo.db.posts
    post_list = reversed(list(posts.find({})))
    posts_by_user = []
    for post in post_list:
        if post['author'] == username:
            posts_by_user.append(post)
    return render_template('profile.html', posts_by_user=posts_by_user, user =mongo.db.users.find_one({'username' : username}))

# LOGOUT
@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash('You are now logged out', 'danger')
    return redirect(url_for('index'))


# Like a post
@app.route('/like/<string:title>', methods = ['GET', 'POST', 'PUT'])
@is_logged_in
def like(title):
    form = Feed(request.form)
    posts = mongo.db.posts
    current_post = posts.find_one({'title':title})
    if 'likes' not in current_post.keys():
        posts.update({'title':title}, {'$inc' : { 'likes' : 1}}, upsert=False)
    else:
        posts.update({'title':title}, {'$inc' : { 'likes' : 1}}, upsert=False)
    post_list = reversed(list(posts.find({})))
    return render_template('feed.html', form=form, posts=post_list, users=mongo.db.users)

# PAGE NOT FOUND
@app.errorhandler(404)
def page_not_found(error):
    return render_template('page_not_found.html'), 404

if __name__ == '__main__':
    app.secret_key = 'likeagirl'
    app.run(port = 2000, debug = True)