from flask import Blueprint, render_template, redirect, url_for, flash, session
from models.user import Notification
from extensions import db

notification_bp = Blueprint('notification', __name__)

@notification_bp.route('/notifications')
def notifications():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    role = session.get('role', 'user')
    name = session.get('name', 'User')
    user_id = session.get('user_id')
    
    notifs = Notification.query.filter_by(user_id=user_id).order_by(Notification.created_at.desc()).all()
    return render_template('notifications.html', role=role, name=name, current_page='notifications', notifications=notifs)

@notification_bp.route('/api/notifications/read_all', methods=['POST'])
def read_all_notifications():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    user_id = session.get('user_id')
    notifs = Notification.query.filter_by(user_id=user_id, is_read=False).all()
    for n in notifs:
        n.is_read = True
    db.session.commit()
    flash('All notifications marked as read.', 'success')
    return redirect(url_for('notification.notifications'))
