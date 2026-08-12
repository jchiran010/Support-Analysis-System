from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from models.user import User
from models.complaint import Complaint
from extensions import db

user_bp = Blueprint('user', __name__)

@user_bp.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    role = session.get('role', 'user')
    name = session.get('name', 'User')
    user_id = session.get('user_id')
    
    stats = {}
    from sqlalchemy import func
    categories = ['Technical Support', 'Billing', 'Feature Request', 'Other']
    cat_counts = []

    if role == 'admin':
        stats['total'] = Complaint.query.count()
        stats['pending'] = Complaint.query.filter_by(status='Pending').count()
        stats['resolved'] = Complaint.query.filter_by(status='Resolved').count()
        stats['high_priority'] = Complaint.query.filter_by(priority='High').count()
        recent_complaints = Complaint.query.order_by(Complaint.created_at.desc()).limit(5).all()
        for cat in categories:
            cat_counts.append(Complaint.query.filter_by(category=cat).count())
        
        trend_query = db.session.query(
            func.date(Complaint.created_at).label('date'),
            func.count(Complaint.id).label('count')
        )
        template_name = 'admin/dashboard.html'
    else:
        stats['my_tickets'] = Complaint.query.filter_by(user_id=user_id).count()
        stats['in_progress'] = Complaint.query.filter_by(user_id=user_id, status='In Progress').count()
        stats['resolved'] = Complaint.query.filter_by(user_id=user_id, status='Resolved').count()
        recent_complaints = Complaint.query.filter_by(user_id=user_id).order_by(Complaint.created_at.desc()).limit(5).all()
        for cat in categories:
            cat_counts.append(Complaint.query.filter_by(user_id=user_id, category=cat).count())
            
        trend_query = db.session.query(
            func.date(Complaint.created_at).label('date'),
            func.count(Complaint.id).label('count')
        ).filter(Complaint.user_id == user_id)
        template_name = 'user-dashboard.html'
        
    trend_data = trend_query.group_by(func.date(Complaint.created_at)).order_by(func.date(Complaint.created_at).asc()).all()
    trend_labels = [row[0] for row in trend_data]
    trend_values = [row[1] for row in trend_data]
    if not trend_labels:
        trend_labels = ['No Data']
        trend_values = [0]

    return render_template(template_name, role=role, name=name, current_page='dashboard', stats=stats, recent_complaints=recent_complaints, cat_counts=cat_counts, trend_labels=trend_labels, trend_values=trend_values)

@user_bp.route('/settings', methods=['GET', 'POST'])
def settings():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
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
                return redirect(url_for('user.settings'))
            user.email = email
            db.session.commit()
            flash('Email updated successfully.', 'success')
            
        if current_password and new_password:
            if not check_password_hash(user.password, current_password):
                flash('Incorrect current password.', 'danger')
                return redirect(url_for('user.settings'))
            user.password = generate_password_hash(new_password)
            db.session.commit()
            flash('Password updated successfully.', 'success')
            
        return redirect(url_for('user.settings'))
    
    template_name = 'admin/settings.html' if role == 'admin' else 'profile.html'
    return render_template(template_name, role=role, name=name, current_page='settings', user=user)

@user_bp.route('/page/<page_name>')
def page(page_name):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    role = session.get('role', 'user')
    name = session.get('name', 'User')
    
    try:
        from jinja2.exceptions import TemplateNotFound
        return render_template(f'{page_name}.html', role=role, name=name, current_page=page_name)
    except TemplateNotFound:
        return render_template('dummy.html', role=role, name=name, page_name=page_name.replace('-', ' ').title(), current_page=page_name)
