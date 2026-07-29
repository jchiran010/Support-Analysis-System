import os
from flask import Flask, render_template, redirect, url_for, request, flash, session, make_response
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from io import StringIO
import csv

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__, 
            template_folder=os.path.join(basedir, '../Frontend/templates'), 
            static_folder=os.path.join(basedir, '../Frontend/static'))

app.config['SECRET_KEY'] = 'enterprise_secret_key_123'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

if os.environ.get('VERCEL'):
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/complaints.db'
else:
    db_dir = os.path.join(basedir, '../Database')
    os.makedirs(db_dir, exist_ok=True)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(db_dir, 'complaints.db')

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='user')
    complaints = db.relationship('Complaint', backref='author', lazy=True)
    notifications = db.relationship('Notification', backref='recipient', lazy=True)

class Complaint(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    priority = db.Column(db.String(20), nullable=False, default='Low')
    status = db.Column(db.String(20), nullable=False, default='Pending')
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.String(255), nullable=False)
    is_read = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

def create_notification(user_id, message):
    try:
        notif = Notification(user_id=user_id, message=message)
        db.session.add(notif)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Error creating notification: {e}")

def seed_data():
    if User.query.count() == 0:
        admin = User(username='admin', email='admin@example.com', password=generate_password_hash('admin'), role='admin')
        user = User(username='user', email='user@example.com', password=generate_password_hash('user'), role='user')
        db.session.add(admin)
        db.session.add(user)
        db.session.commit()
        
        c1 = Complaint(title='Login Issue', description='Cannot login to the portal.', category='Technical Support', priority='High', status='Pending', author=user)
        c2 = Complaint(title='Billing Error', description='Charged twice for the subscription.', category='Billing', priority='Medium', status='In Progress', author=user)
        c3 = Complaint(title='Feature Request', description='Please add dark mode.', category='Feature Request', priority='Low', status='Resolved', author=user)
        db.session.add_all([c1, c2, c3])
        db.session.commit()

        # Seed sample notifications
        n1 = Notification(message='Welcome to Support Analysis System! Feel free to raise a ticket.', user_id=user.id)
        n2 = Notification(message='Admin updated ticket #TKT-3 to Resolved.', user_id=user.id)
        n3 = Notification(message='New ticket submitted: #TKT-1 ("Login Issue").', user_id=admin.id)
        db.session.add_all([n1, n2, n3])
        db.session.commit()

with app.app_context():
    db.create_all()
    seed_data()

@app.route('/')
def splash():
    return render_template('splash.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['role'] = user.role
            session['name'] = user.username.title()
            return redirect(url_for('dashboard'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return redirect(url_for('signup'))
        
        if User.query.filter_by(username=username).first():
            flash('Username already taken. Please choose another.', 'danger')
            return redirect(url_for('signup'))
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered. Please use another.', 'danger')
            return redirect(url_for('signup'))
        
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
        return redirect(url_for('login'))
    
    return render_template('signup.html')

@app.context_processor
def inject_notifications_count():
    count = 0
    if 'user_id' in session:
        count = Notification.query.filter_by(user_id=session['user_id'], is_read=False).count()
    return dict(unread_notifications_count=count)

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    role = session.get('role', 'user')
    name = session.get('name', 'User')
    user_id = session.get('user_id')
    
    stats = {}
    if role == 'admin':
        stats['total'] = Complaint.query.count()
        stats['pending'] = Complaint.query.filter_by(status='Pending').count()
        stats['resolved'] = Complaint.query.filter_by(status='Resolved').count()
        stats['high_priority'] = Complaint.query.filter_by(priority='High').count()
        recent_complaints = Complaint.query.order_by(Complaint.created_at.desc()).limit(5).all()
    else:
        stats['my_tickets'] = Complaint.query.filter_by(user_id=user_id).count()
        stats['in_progress'] = Complaint.query.filter_by(user_id=user_id, status='In Progress').count()
        stats['resolved'] = Complaint.query.filter_by(user_id=user_id, status='Resolved').count()
        recent_complaints = Complaint.query.filter_by(user_id=user_id).order_by(Complaint.created_at.desc()).limit(5).all()
        
    # Chart Data for Dashboard
    from sqlalchemy import func
    categories = ['Technical Support', 'Billing', 'Feature Request', 'Other']
    cat_counts = []
    for cat in categories:
        if role == 'admin':
            cat_counts.append(Complaint.query.filter_by(category=cat).count())
        else:
            cat_counts.append(Complaint.query.filter_by(user_id=user_id, category=cat).count())
            
    trend_query = db.session.query(
        func.date(Complaint.created_at).label('date'),
        func.count(Complaint.id).label('count')
    )
    if role != 'admin':
        trend_query = trend_query.filter(Complaint.user_id == user_id)
        
    trend_data = trend_query.group_by(func.date(Complaint.created_at)).order_by(func.date(Complaint.created_at).asc()).all()
    trend_labels = [row[0] for row in trend_data]
    trend_values = [row[1] for row in trend_data]
    if not trend_labels:
        trend_labels = ['No Data']
        trend_values = [0]

    return render_template('dashboard.html', role=role, name=name, current_page='dashboard', stats=stats, recent_complaints=recent_complaints, cat_counts=cat_counts, trend_labels=trend_labels, trend_values=trend_values)

@app.route('/complaints')
def complaints():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    role = session.get('role', 'user')
    name = session.get('name', 'User')
    user_id = session.get('user_id')
    
    if role == 'admin':
        complaint_list = Complaint.query.order_by(Complaint.created_at.desc()).all()
    else:
        complaint_list = Complaint.query.filter_by(user_id=user_id).order_by(Complaint.created_at.desc()).all()
        
    return render_template('complaints.html', role=role, name=name, current_page='complaints', complaints=complaint_list)

@app.route('/api/complaints/add', methods=['POST'])
def add_complaint():
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    title = request.form.get('title')
    description = request.form.get('description')
    category = request.form.get('category')
    priority = request.form.get('priority', 'Low')
    
    new_complaint = Complaint(
        title=title, 
        description=description, 
        category=category, 
        priority=priority, 
        user_id=session['user_id']
    )
    db.session.add(new_complaint)
    db.session.commit()
    create_notification(session['user_id'], f'Your ticket #TKT-{new_complaint.id} ("{new_complaint.title}") has been submitted.')
    admins = User.query.filter_by(role='admin').all()
    for admin in admins:
        create_notification(admin.id, f'New ticket submitted: #TKT-{new_complaint.id} by {session["name"]}.')
    flash('Complaint submitted successfully.', 'success')
    return redirect(url_for('complaints'))

@app.route('/api/complaints/update_status/<int:complaint_id>', methods=['POST'])
def update_status(complaint_id):
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))
        
    new_status = request.form.get('status')
    complaint = Complaint.query.get_or_404(complaint_id)
    complaint.status = new_status
    db.session.commit()
    create_notification(complaint.user_id, f'Your ticket #TKT-{complaint.id} status was updated to "{new_status}" by Admin.')
    flash(f'Status updated to {new_status}.', 'success')
    return redirect(url_for('complaints'))

@app.route('/notifications')
def notifications():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    role = session.get('role', 'user')
    name = session.get('name', 'User')
    user_id = session.get('user_id')
    
    notifs = Notification.query.filter_by(user_id=user_id).order_by(Notification.created_at.desc()).all()
    return render_template('notifications.html', role=role, name=name, current_page='notifications', notifications=notifs)

@app.route('/api/notifications/read_all', methods=['POST'])
def read_all_notifications():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user_id = session.get('user_id')
    notifs = Notification.query.filter_by(user_id=user_id, is_read=False).all()
    for n in notifs:
        n.is_read = True
    db.session.commit()
    flash('All notifications marked as read.', 'success')
    return redirect(url_for('notifications'))

@app.route('/users')
def users():
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))
    role = session.get('role', 'user')
    name = session.get('name', 'User')
    
    user_list = User.query.order_by(User.id.asc()).all()
    return render_template('users.html', role=role, name=name, current_page='users', users=user_list)

@app.route('/api/users/change_role/<int:user_id>', methods=['POST'])
def change_role(user_id):
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))
    if user_id == session['user_id']:
        flash('You cannot change your own role.', 'danger')
        return redirect(url_for('users'))
        
    user = User.query.get_or_404(user_id)
    user.role = 'admin' if user.role == 'user' else 'user'
    db.session.commit()
    flash(f'Role for {user.username} updated to {user.role.upper()}.', 'success')
    return redirect(url_for('users'))

@app.route('/api/users/delete/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))
    if user_id == session['user_id']:
        flash('You cannot delete your own account.', 'danger')
        return redirect(url_for('users'))
        
    user = User.query.get_or_404(user_id)
    Complaint.query.filter_by(user_id=user_id).delete()
    Notification.query.filter_by(user_id=user_id).delete()
    db.session.delete(user)
    db.session.commit()
    flash(f'User {user.username} deleted.', 'success')
    return redirect(url_for('users'))

@app.route('/reports')
def reports():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    role = session.get('role', 'user')
    name = session.get('name', 'User')
    user_id = session.get('user_id')
    
    status_filter = request.args.get('status')
    priority_filter = request.args.get('priority')
    category_filter = request.args.get('category')
    
    query = Complaint.query
    if role != 'admin':
        query = query.filter_by(user_id=user_id)
        
    if status_filter:
        query = query.filter_by(status=status_filter)
    if priority_filter:
        query = query.filter_by(priority=priority_filter)
    if category_filter:
        query = query.filter_by(category=category_filter)
        
    complaints_list = query.order_by(Complaint.created_at.desc()).all()
    
    return render_template(
        'reports.html', 
        role=role, 
        name=name, 
        current_page='reports', 
        complaints=complaints_list,
        status_filter=status_filter,
        priority_filter=priority_filter,
        category_filter=category_filter
    )

@app.route('/reports/export')
def export_reports():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    role = session.get('role', 'user')
    user_id = session.get('user_id')
    
    status_filter = request.args.get('status')
    priority_filter = request.args.get('priority')
    category_filter = request.args.get('category')
    
    query = Complaint.query
    if role != 'admin':
        query = query.filter_by(user_id=user_id)
        
    if status_filter:
        query = query.filter_by(status=status_filter)
    if priority_filter:
        query = query.filter_by(priority=priority_filter)
    if category_filter:
        query = query.filter_by(category=category_filter)
        
    complaints_list = query.order_by(Complaint.created_at.desc()).all()
    
    si = StringIO()
    cw = csv.writer(si)
    cw.writerow(['Ticket ID', 'Title', 'Description', 'Category', 'Priority', 'Status', 'Date', 'Customer'])
    for c in complaints_list:
        cw.writerow([
            f'#TKT-{c.id}',
            c.title,
            c.description,
            c.category,
            c.priority,
            c.status,
            c.created_at.strftime('%Y-%m-%d %H:%M'),
            c.author.username
        ])
        
    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename=complaints_report.csv"
    output.headers["Content-type"] = "text/csv"
    return output

@app.route('/analytics')
def analytics():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    role = session.get('role', 'user')
    name = session.get('name', 'User')
    user_id = session.get('user_id')
    
    categories = ['Technical Support', 'Billing', 'Feature Request', 'Other']
    cat_counts = []
    for cat in categories:
        if role == 'admin':
            count = Complaint.query.filter_by(category=cat).count()
        else:
            count = Complaint.query.filter_by(user_id=user_id, category=cat).count()
        cat_counts.append(count)
        
    statuses = ['Pending', 'In Progress', 'Resolved']
    status_counts = []
    for stat in statuses:
        if role == 'admin':
            count = Complaint.query.filter_by(status=stat).count()
        else:
            count = Complaint.query.filter_by(user_id=user_id, status=stat).count()
        status_counts.append(count)
        
    from sqlalchemy import func
    trend_query = db.session.query(
        func.date(Complaint.created_at).label('date'),
        func.count(Complaint.id).label('count')
    )
    if role != 'admin':
        trend_query = trend_query.filter(Complaint.user_id == user_id)
        
    trend_data = trend_query.group_by(func.date(Complaint.created_at)).order_by(func.date(Complaint.created_at).asc()).all()
    
    trend_labels = [row[0] for row in trend_data]
    trend_values = [row[1] for row in trend_data]
    
    if not trend_labels:
        trend_labels = ['No Data']
        trend_values = [0]
        
    return render_template(
        'analytics.html',
        role=role,
        name=name,
        current_page='analytics',
        categories=categories,
        cat_counts=cat_counts,
        statuses=statuses,
        status_counts=status_counts,
        trend_labels=trend_labels,
        trend_values=trend_values
    )

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    role = session.get('role', 'user')
    name = session.get('name', 'User')
    user_id = session.get('user_id')
    
    user = User.query.get_or_404(user_id)
    
    if request.method == 'POST':
        email = request.form.get('email')
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        
        if email and email != user.email:
            existing_email = User.query.filter_by(email=email).first()
            if existing_email:
                flash('Email already in use.', 'danger')
                return redirect(url_for('settings'))
            user.email = email
            db.session.commit()
            flash('Email updated successfully.', 'success')
            
        if current_password and new_password:
            if not check_password_hash(user.password, current_password):
                flash('Incorrect current password.', 'danger')
                return redirect(url_for('settings'))
            user.password = generate_password_hash(new_password)
            db.session.commit()
            flash('Password updated successfully.', 'success')
            
        return redirect(url_for('settings'))
        
    return render_template('settings.html', role=role, name=name, current_page='settings', user=user)

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
