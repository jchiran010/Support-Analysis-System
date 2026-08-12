from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from models.complaint import Complaint
from models.user import User, Notification
from extensions import db

complaint_bp = Blueprint('complaint', __name__)

def create_notification(user_id, message):
    try:
        notif = Notification(user_id=user_id, message=message)
        db.session.add(notif)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Error creating notification: {e}")

@complaint_bp.route('/complaints')
def complaints():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    role = session.get('role', 'user')
    name = session.get('name', 'User')
    user_id = session.get('user_id')
    
    if role == 'admin':
        complaint_list = Complaint.query.order_by(Complaint.created_at.desc()).all()
        template_name = 'admin/complaints.html'
    else:
        complaint_list = Complaint.query.filter_by(user_id=user_id).order_by(Complaint.created_at.desc()).all()
        template_name = 'complaint-history.html'
        
    return render_template(template_name, role=role, name=name, current_page='complaints', complaints=complaint_list)

@complaint_bp.route('/api/complaints/add', methods=['POST'])
def add_complaint():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
        
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
    return redirect(url_for('complaint.complaints'))

@complaint_bp.route('/api/complaints/update_status/<int:complaint_id>', methods=['POST'])
def update_status(complaint_id):
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('auth.login'))
        
    new_status = request.form.get('status')
    complaint = Complaint.query.get_or_404(complaint_id)
    complaint.status = new_status
    db.session.commit()
    create_notification(complaint.user_id, f'Your ticket #TKT-{complaint.id} status was updated to "{new_status}" by Admin.')
    flash(f'Status updated to {new_status}.', 'success')
    return redirect(url_for('complaint.complaints'))
