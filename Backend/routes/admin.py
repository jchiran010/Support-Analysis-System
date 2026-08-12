from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from models.user import User, Notification
from models.complaint import Complaint
from extensions import db

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/users')
def users():
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('auth.login'))
    role = session.get('role', 'user')
    name = session.get('name', 'User')
    
    user_list = User.query.order_by(User.id.asc()).all()
    return render_template('admin/users.html', role=role, name=name, current_page='users', users=user_list)

@admin_bp.route('/api/users/change_role/<int:user_id>', methods=['POST'])
def change_role(user_id):
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('auth.login'))
    if user_id == session['user_id']:
        flash('You cannot change your own role.', 'danger')
        return redirect(url_for('admin.users'))
        
    user = User.query.get_or_404(user_id)
    user.role = 'admin' if user.role == 'user' else 'user'
    db.session.commit()
    flash(f'Role for {user.username} updated to {user.role.upper()}.', 'success')
    return redirect(url_for('admin.users'))

@admin_bp.route('/api/users/delete/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('auth.login'))
    if user_id == session['user_id']:
        flash('You cannot delete your own account.', 'danger')
        return redirect(url_for('admin.users'))
        
    user = User.query.get_or_404(user_id)
    Complaint.query.filter_by(user_id=user_id).delete()
    Notification.query.filter_by(user_id=user_id).delete()
    db.session.delete(user)
    db.session.commit()
    flash(f'User {user.username} deleted.', 'success')
    return redirect(url_for('admin.users'))
