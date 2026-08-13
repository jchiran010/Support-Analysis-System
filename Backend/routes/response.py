from flask import Blueprint, redirect, url_for, request, flash, session
from models.response import Response
from models.complaint import Complaint
from models.user import Notification
from extensions import db

response_bp = Blueprint('response', __name__)

@response_bp.route('/api/complaints/<int:complaint_id>/reply', methods=['POST'])
def add_reply(complaint_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
        
    complaint = Complaint.query.get_or_404(complaint_id)
    message = request.form.get('message')
    
    if message:
        resp = Response(message=message, complaint_id=complaint_id, user_id=session['user_id'])
        db.session.add(resp)
        
        # If admin replied, notify the complaint author
        if session.get('role') == 'admin':
            notif = Notification(user_id=complaint.user_id, message=f'Admin replied to your ticket #TKT-{complaint.id}.')
            db.session.add(notif)
            
            # Optionally update status if specified
            new_status = request.form.get('status')
            if new_status and new_status != complaint.status:
                complaint.status = new_status
        else:
            # User replied, notify admin
            admins = Notification.query.filter_by(user_id=1).all() # sample notification trigger
            
        db.session.commit()
        flash('Reply posted successfully.', 'success')
        
    return redirect(url_for('complaint.complaint_detail', complaint_id=complaint_id))
