import os
import sys

basedir = os.path.abspath(os.path.dirname(__file__))
if basedir not in sys.path:
    sys.path.append(basedir)

from flask import Flask
from extensions import db
from werkzeug.security import generate_password_hash
from models.user import User, Notification
from models.complaint import Complaint


def create_app():
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

    db.init_app(app)

    with app.app_context():
        db.create_all()
        seed_data()

    # Context processor
    @app.context_processor
    def inject_notifications_count():
        from flask import session
        count = 0
        if 'user_id' in session:
            count = Notification.query.filter_by(user_id=session['user_id'], is_read=False).count()
        return dict(unread_notifications_count=count)

    # Register blueprints
    from routes.auth import auth_bp
    from routes.user import user_bp
    from routes.complaint import complaint_bp
    from routes.admin import admin_bp
    from routes.notification import notification_bp
    from routes.report import report_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(complaint_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(notification_bp)
    app.register_blueprint(report_bp)

    return app

def seed_data():
    if User.query.count() == 0:
        admin = User(username='admin', email='admin@example.com', password=generate_password_hash('admin'), role='admin') # type: ignore
        user = User(username='user', email='user@example.com', password=generate_password_hash('user'), role='user') # type: ignore
        db.session.add(admin)
        db.session.add(user)
        db.session.commit()
        
        c1 = Complaint(title='Login Issue', description='Cannot login to the portal.', category='Technical Support', priority='High', status='Pending', author=user) # type: ignore
        c2 = Complaint(title='Billing Error', description='Charged twice for the subscription.', category='Billing', priority='Medium', status='In Progress', author=user) # type: ignore
        c3 = Complaint(title='Feature Request', description='Please add dark mode.', category='Feature Request', priority='Low', status='Resolved', author=user) # type: ignore
        db.session.add_all([c1, c2, c3])
        db.session.commit()

        n1 = Notification(message='Welcome to Support Analysis System! Feel free to raise a ticket.', user_id=user.id) # type: ignore
        n2 = Notification(message='Admin updated ticket #TKT-3 to Resolved.', user_id=user.id) # type: ignore
        n3 = Notification(message='New ticket submitted: #TKT-1 ("Login Issue").', user_id=admin.id) # type: ignore
        db.session.add_all([n1, n2, n3])
        db.session.commit()

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, port=5000)
