from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy
import http.cookies


app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:bloggerboi@localhost:3306/blogz'
app.config['SQLALCHEMY_ECHO'] = True

db = SQLAlchemy(app)

logged_in = False
userpost = 0
user_name = ''

class Posts(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(250))
    userID = db.Column(db.Integer, db.ForeignKey('users.userID'), nullable=False)

    def __init__(self, title, body, userID):
        self.title = title
        self.body = body
        self.userID = userID

class Users(db.Model):
    userID = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20))
    password = db.Column(db.String(20))
    posts = db.relationship('Posts', backref='users', lazy=True)

    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.route('/', methods=['GET'])
def index():   
    global logged_in
    users = Users.query.all()
    return render_template('frontpage.html', users=users, loggedin=logged_in)

@app.route('/newpost', methods=['GET'])
def newpost():
    global logged_in
    return render_template('newentry.html', loggedin=logged_in)


@app.route('/newpostlogic', methods=['POST'])
def newpostlogic():
    global logged_in
    if logged_in == False:
        return redirect('/signup')

    title = request.form['title']
    body = request.form['body']
    


    if title == "" or body == "":
        return render_template('newentry.html', error='Please fill out both fields.', loggedin=logged_in)
    elif len(body) > 250:
        return render_template('newentry.html', error='Max 250 characters in post.', loggedin=logged_in)
   
    post = Posts(title, body, userpost)
    
    
    db.session.add(post)
    db.session.commit()
    return render_template('/blogentry?id='+str(post.id), loggedin=logged_in)

@app.route('/user', methods=['GET'])
def mainblog():
    global logged_in
    userid = request.args.get('username')
    posts = Posts.query.filter_by(userID=user.userID).all()
    return render_template('/user?userID=' + str(user.userID), posts=posts, loggedin=logged_in, username=userid.username)

@app.route('/blogentry', methods=['GET'])
def postclicked():
    global logged_in
    postid = request.args.get('id')
    post = Posts.query.filter_by(id=postid).first()
    return render_template('entry.html', post=post, loggedin=logged_in)

@app.route('/signup', methods=['GET'])
def register():
    return render_template('register.html')

@app.route('/login', methods=['GET'])
def login():
    return render_template('login.html')

@app.route('/allposts', methods=['GET'])
def allposts():    
    global logged_in
    posts = Posts.query.filter_by().all()
    return render_template('index.html', posts=posts, loggedin=logged_in)

@app.route('/loginlogic', methods=['POST'])
def loginlogic():
    global user_name
    global userpost
    username = request.form['username']
    user_name = request.form['username']
    password = request.form['password']
    error = 'Username or password is invalid. Please try again.'
    global logged_in

    userlogin = Users.query.filter_by(username=username).first()
    userpost = userlogin.userID

    if username == '' or password == '':
        return render_template('login.html', error=error)
    elif userlogin == None:
        return render_template('login.html', error=error)
    
    if password != userlogin.password:
        return render_template('login.html', error=error)
    else:
        logged_in = userlogin.userID
        return render_template('frontpage.html', loggedin=logged_in)

@app.route('/registerlogic', methods=['POST'])
def registerlogic():
    username = request.form['newusername']
    password = request.form['newpassword']
    verified = request.form['verifypass']
    error = 'Username or password is invalid. Please try again.'
    


    if username == '' or password == '':
        return render_template('register.html', error=error)
        if verified == '':
            return render_template('register.html', error='Please verify your password')
    if len(username) > 20 or len(password) > 20:
        return render_template('register.html', error='No more than 20 characters in the either field')
    if verified != password:
        return render_template('register.html', error='Passwords do not match')


    user = Users(username, password)
    db.session.add(user)
    db.session.commit()
    return redirect('/user?userID=' + str(user.userID))

@app.route('/logout', methods=['GET'])
def logout():
    global logged_in
    logged_in = False
    return redirect('/')




if __name__ == '__main__':
    app.run()