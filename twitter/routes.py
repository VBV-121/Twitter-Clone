import secrets
import os
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort
from twitter import app, db, bcrypt, mail
from twitter.forms import RegistrationForm, LoginForm, UpdateAccountForm, TweetForm, RequestResetForm, ResetPasswordForm, MessageForm
from flask_mail import Message
from twitter.models import User, Post, ChatMessages, Bookmark
from flask_login import login_user, current_user, logout_user, login_required

@app.route("/")

@app.route("/home",methods=['GET','POST'])
def home():
	form = TweetForm()
	if form.validate_on_submit():
		post = Post(content=form.content.data, author= current_user)
		db.session.add(post)
		db.session.commit()
		print('got in home')
		flash(f'Your tweet has been posted!','success')
		return redirect(url_for('home'))
	page = request.args.get('page',1,type=int)
	posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
	return render_template("home.html",posts=posts,form=form)

@app.route("/about")
def about():
	return render_template("about.html",title="About")

@app.route('/register',methods=['GET','POST'])
def register():
	form=RegistrationForm()
	if current_user.is_authenticated:
		return redirect(url_for('home'))
	if form.validate_on_submit():
		hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
		user = User(username=form.username.data, email = form.email.data, password=hashed_password)
		db.session.add(user)
		db.session.commit()
		flash(f'Account created for { form.username.data }!','success')
		return redirect(url_for('login'))
	return render_template('register.html',title='Register',form=form)

@app.route('/login',methods=['GET','POST'])
def login():
	form=LoginForm()
	if current_user.is_authenticated:
		return redirect(url_for('home'))
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first()
		if user and bcrypt.check_password_hash(user.password, form.password.data):
			login_user(user, remember = form.remember.data)
			next_page = request.args.get('next')
			return redirect(next_page) if next_page else redirect(url_for('home'))
		else:
			flash('Login Unsuccessful. Please check Email ID or Password.','danger')
	return render_template('login.html',title='Login',form=form)

@app.route('/logout')
def logout():
	logout_user()
	return redirect(url_for('home'))

def save_picture(form_picture):
	random_hex = secrets.token_hex(8)
	_,f_ext = os.path.splitext(form_picture.filename)
	picture_fn = random_hex + f_ext
	picture_path = os.path.join(app.root_path,'static/profile_pics',picture_fn)
	output_size = (125,125)
	i=Image.open(form_picture)
	i.thumbnail(output_size)
	i.save(picture_path)
	return picture_fn

@app.route('/profile',methods=['GET','POST'])
@login_required
def profile():
	form = UpdateAccountForm()
	if form.validate_on_submit():
		if form.picture.data:
			if form.picture.data.filename == "default.jpg":
				current_user.image_file = "default.jpg"
			else:
				picture_file = save_picture(form.picture.data)
				current_user.image_file = picture_file
		current_user.username = form.username.data
		current_user.email = form.email.data
		db.session.commit()
		flash('Your account has been updated successfully!','success')
		return redirect(url_for('profile'))
	elif request.method == 'GET':
		form.username.data = current_user.username
		form.email.data = current_user.email
	image_file = url_for('static',filename='profile_pics/'+current_user.image_file)
	return render_template('profile.html',title='Profile', image_file=image_file,form=form)

@app.route('/tweet/new',methods=['GET','POST'])
@login_required
def new_tweet():
	form = TweetForm()
	if form.validate_on_submit():
		post = Post(content=form.content.data, author= current_user)
		db.session.add(post)
		db.session.commit()
		flash(f'Your tweet has been posted!','success')
		return redirect(url_for('home'))
	return render_template('create_tweet.html',title='New Tweet', form=form , legend='New Tweet')

@app.route('/tweet/<int:post_id>')
def tweet(post_id):
	post = Post.query.get_or_404(post_id)
	return render_template('tweet.html',title="Tweet",post=post)

@app.route('/tweet/<int:post_id>/update',methods=['GET','POST'])
@login_required
def update_tweet(post_id):
	post = Post.query.get_or_404(post_id)
	if post.author != current_user:
		abort(403)
	form = TweetForm()
	if form.validate_on_submit():
		post.content = form.content.data
		db.session.commit()
		flash('Your tweet has been updated!','success')
		return redirect(url_for('tweet',post_id=post.id))
	elif request.method == 'GET':
		form.content.data = post.content
	return render_template('create_tweet.html',title='Update Tweet', form=form, legend='Update Tweet')

@app.route("/post/<int:post_id>/delete",methods=['POST'])
@login_required
def delete_tweet(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted!','success')
    return redirect(url_for('home'))

@app.route("/user/<string:username>")
@login_required
def user_tweets(username):
    page = request.args.get('page',1,type=int)
    user=User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user).order_by(Post.date_posted.desc()).paginate(page=page,per_page=3)
    return render_template("user_tweets.html",posts=posts,user=user)

@app.route("/explore")
def explore():
	return render_template("explore.html",title="Explore")

@app.route("/notifications")
def notifications():
	return render_template("notifications.html",title="Notification")

@app.route("/messages")
@login_required
def messages():
	user = User.query.all()
	return render_template("messages.html",title="Messages",user=user)

@app.route("/chatroom/<string:username>",methods=['GET','POST'])
@login_required
def chat_room(username):
	form = MessageForm()
	if form.validate_on_submit():
		post = ChatMessages(msg=form.msg.data, sender_text= current_user.username,receiver_text=username)
		db.session.add(post)
		db.session.commit()
		print(username)
		flash(f'Your message has been posted!','success')
		return redirect(url_for('chat_room',username=username))
	elif request.method == 'GET':
		total=[]
		sender=ChatMessages.query.filter_by(sender_text=current_user.username).all()
		receiver=ChatMessages.query.filter_by(sender_text=username).all()
		total = sender + receiver
		for i in range(0,len(total)):
			for j in range(i,len(total)):
				if total[i].date_posted<total[j].date_posted:
					total[i],total[j]=total[j],total[i]
		total = total[::-1]
		print(total)
		return render_template('chat_room.html',title='Chat Room', form=form , legend='Chat Room',total=total)

@app.route("/bookmarks")
def bookmarks():
	posts=[]
	users=[]
	bookmark = Bookmark.query.all()
	for i in bookmark:
		if i.user_id == current_user.id:
			temp=Post.query.filter_by(id=i.post_id).first()
			if temp.content not in posts:
				posts.append(temp.content)
				temp1=User.query.filter_by(id= i.user_id).first()
				users.append(temp1)
	return render_template('bookmarks.html',title="Bookmark",posts=posts,users=users)

@app.route("/lists")
def lists():
	return render_template("lists.html",title="Lists")

def send_reset_email(user):
	token = user.get_rest_token()
	msg = Message('Password Reset Request', sender='vghadiali18@gmail.com', recipients=[user.email])
	msg.body = f''' To reset your password, visit the following link:
{url_for('reset_token', token=token,_external= True)}
'''
	mail.send(msg)


@app.route("/reset_password", methods=['GET','POST'])
def reset_request():
	if current_user.is_authenticated:
		return redirect(url_for('home'))
	form = RequestResetForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first()
		send_reset_email(user)
		flash('An email has been sent with instructions to reset password','info')
		return redirect(url_for('login'))
	return render_template('reset_request.html', title='Reset Password', form = form)

@app.route("/reset_password/<token>", methods=['GET','POST'])
def reset_token(token):
	if current_user.is_authenticated:
		return redirect(url_for('home'))
	user = User.verify_reset_token(token)
	if user is None:
		flash('That is an invalid or expired token','warning')
		return redirect(url_for('reset_request'))
	form = ResetPasswordForm()
	if form.validate_on_submit():
		hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
		user.password = hashed_password
		db.session.commit()
		flash(f'Password Updated!','success')
		return redirect(url_for('login'))
	return render_template('reset_token.html', title='Reset Password',form=form)

@app.route("/tweet/<int:post_id>/bookmark",methods=['GET','POST'])
@login_required
def bookmark_save(post_id):
	post = Post.query.get_or_404(post_id)
	if post:
		bookmark = Bookmark(post_id=post_id, user_id=current_user.id)
		db.session.add(bookmark)
		db.session.commit()
		flash(f'New bookmark added','success')
		return render_template('bookmarks.html',title="Bookmark")
	#elif request.method == 'GET':
