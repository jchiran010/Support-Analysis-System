from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from models.feedback import Feedback
from extensions import db

feedback_bp = Blueprint('feedback', __name__)

@feedback_bp.route('/feedback', methods=['GET', 'POST'])
def feedback_page():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
        
    role = session.get('role', 'user')
    name = session.get('name', 'User')
    user_id = session.get('user_id')
    
    if request.method == 'POST':
        rating = request.form.get('rating', type=int)
        comment = request.form.get('comments') or request.form.get('comment')
        
        if rating:
            fb = Feedback(rating=rating, comment=comment, user_id=user_id)
            db.session.add(fb)
            db.session.commit()
            flash('Thank you! Your feedback has been submitted successfully.', 'success')
            return redirect(url_for('feedback.feedback_page'))
        else:
            flash('Please select a star rating.', 'danger')
            
    feedbacks_list = []
    if role == 'admin':
        feedbacks_list = Feedback.query.order_by(Feedback.created_at.desc()).all()
        
    return render_template('feedback.html', role=role, name=name, current_page='feedback', feedbacks=feedbacks_list)
