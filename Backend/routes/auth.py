from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from models.user import User, Notification
from extensions import db

auth_bp = Blueprint('auth', __name__)

def create_notification(user_id, message):
    try:
        notif = Notification(user_id=user_id, message=message)
        db.session.add(notif)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Error creating notification: {e}")

@auth_bp.route('/')
def splash():
    return render_template('index.html') # renamed from splash.html

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['role'] = user.role
            session['name'] = user.username.title()
            return redirect(url_for('user.dashboard'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST']) # renamed from /signup
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return redirect(url_for('auth.register'))
        
        if User.query.filter_by(username=username).first():
            flash('Username already taken. Please choose another.', 'danger')
            return redirect(url_for('auth.register'))
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered. Please use another.', 'danger')
            return redirect(url_for('auth.register'))
        
        new_user = User(
            username=username,
            email=email,
            password=generate_password_hash(password),
            role='user'
        )
        db.session.add(new_user)
        db.session.commit()
        create_notification(new_user.id, 'Welcome to Support Analysis System! Your account is active.')
        
        flash('Account created successfully. Please sign in.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('register.html') # renamed from signup.html

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))
