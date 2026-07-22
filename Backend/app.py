import os
from flask import Flask, render_template, redirect, url_for, request, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

app = Flask(__name__, 
            template_folder='../Frontend/templates', 
            static_folder='../Frontend/static')

app.config['SECRET_KEY'] = 'enterprise_secret_key_123'
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, '../Database/complaints.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)

with app.app_context():
    db.create_all()

@app.route('/')
def splash():
    return render_template('splash.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Simple role-based auth for demo
        if username == 'admin' and password == 'admin':
            session['user_id'] = 1
            session['role'] = 'admin'
            session['name'] = 'Admin User'
            return redirect(url_for('dashboard'))
        elif username == 'user' and password == 'user':
            session['user_id'] = 2
            session['role'] = 'user'
            session['name'] = 'Standard User'
            return redirect(url_for('dashboard'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    role = session.get('role', 'user')
    name = session.get('name', 'User')
    return render_template('dashboard.html', role=role, name=name, current_page='dashboard')

@app.route('/page/<page_name>')
def page(page_name):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    role = session.get('role', 'user')
    name = session.get('name', 'User')
    return render_template('dummy.html', role=role, name=name, page_name=page_name.replace('-', ' ').title(), current_page=page_name)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)
