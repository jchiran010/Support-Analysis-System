from flask import Blueprint, render_template, redirect, url_for, request, session, make_response
from models.complaint import Complaint
import csv
from io import StringIO
from extensions import db

report_bp = Blueprint('report', __name__)

@report_bp.route('/reports')
def reports():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
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
    
    template_name = 'admin/reports.html' if role == 'admin' else 'reports.html'
    return render_template(
        template_name, 
        role=role, 
        name=name, 
        current_page='reports', 
        complaints=complaints_list,
        status_filter=status_filter,
        priority_filter=priority_filter,
        category_filter=category_filter
    )

@report_bp.route('/reports/export')
def export_reports():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
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

@report_bp.route('/analytics')
def analytics():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
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
        
    template_name = 'admin/analytics.html' if role == 'admin' else 'analytics.html'
    return render_template(
        template_name,
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
