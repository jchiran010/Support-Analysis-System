# Support Analysis System - Development Guide

## Quick Start

### Prerequisites
- Python 3.13.7 or higher
- VS Code with recommended extensions

### Setup & Run
```bash
cd "c:\Complaint System\Support Analysis System"
pip install -r requirements.txt
python Backend/app.py
```

Access at: `http://localhost:5000`

---

## Architecture Overview

### Model Layer (Backend/models/)
```
User
├── username (unique)
├── email (unique)
├── password (hashed)
└── role (admin/user)

Complaint
├── title
├── description
├── category (Technical Support, Billing, Feature Request, Other)
├── priority (Low, Medium, High)
├── status (Pending, In Progress, Resolved)
├── sentiment (Positive, Negative, Urgent, Neutral)
├── created_at
└── user_id (FK)

Notification
├── message
├── is_read
├── created_at
└── user_id (FK)

Response
├── message
├── created_at
├── complaint_id (FK)
└── user_id (FK)

Feedback
├── rating (1-5)
├── comment
├── created_at
└── user_id (FK)

AuditLog
├── action
├── details
├── created_at
└── user_id (FK)
```

### Route Layer (Backend/routes/)

**auth.py** - Authentication
- `/` - Splash page
- `/login` - Login endpoint
- `/register` - User registration
- `/logout` - Logout

**user.py** - User operations
- `/dashboard` - User/Admin dashboard
- `/settings` - User settings
- `/page/<name>` - Dynamic pages

**complaint.py** - Complaint management
- `/complaints` - List complaints
- `/complaint/<id>` - Complaint details
- `/submit-complaint` - Submit form
- `/api/complaints/add` - Add complaint
- `/api/complaints/update_status/<id>` - Update status
- `/api/search` - Live search
- `/faq` - FAQ page

**admin.py** - Admin operations
- `/users` - User management
- `/api/users/change_role/<id>` - Change user role
- `/api/users/delete/<id>` - Delete user

**notification.py** - Notifications
- `/notifications` - View notifications
- `/api/notifications/read_all` - Mark all as read

**report.py** - Reports & Analytics
- `/reports` - Reports page
- `/reports/export` - Export CSV
- `/analytics` - Analytics dashboard

**response.py** - Complaint responses
- `/api/complaints/<id>/reply` - Add reply

**feedback.py** - Feedback
- `/feedback` - Feedback page
- `POST /feedback` - Submit feedback

---

## File Organization

```
Backend/
├── app.py                 # Main Flask app & initialization
├── config.py             # Configuration (empty - can be populated)
├── extensions.py         # SQLAlchemy instance
├── models/
│   ├── user.py          # User & Notification models
│   ├── complaint.py      # Complaint model
│   ├── response.py       # Response model
│   ├── feedback.py       # Feedback model
│   ├── audit.py         # AuditLog model
│   ├── category.py      # Empty placeholder
│   ├── ticket.py        # Empty placeholder
│   └── admin.py         # Empty placeholder
├── routes/
│   ├── auth.py          # Authentication routes
│   ├── user.py          # User routes
│   ├── complaint.py      # Complaint routes
│   ├── admin.py         # Admin routes
│   ├── notification.py   # Notification routes
│   ├── report.py        # Reports & Analytics
│   ├── response.py       # Response routes
│   └── feedback.py       # Feedback routes
├── services/            # Service layer (utility classes)
└── utils/               # Helper functions

Frontend/
├── templates/
│   ├── base.html        # Base template
│   ├── index.html       # Home page
│   ├── login.html       # Login page
│   ├── register.html    # Registration page
│   └── admin/           # Admin templates
└── static/
    ├── css/             # Stylesheets
    ├── js/              # JavaScript modules
    └── images/          # Images and icons

Database/
├── schema.sql           # Database schema
├── sample_data.sql      # Sample data
└── complaints.db        # SQLite database (auto-created)
```

---

## Environment Setup

### 1. Virtual Environment (Optional but Recommended)
```bash
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure IDE (VS Code)
Extensions are already configured in `.vscode/extensions.json`:
- Python extension
- Pylance for type checking
- Jupyter for notebooks
- SQLite viewer

Settings in `.vscode/settings.json` include extra paths for imports.

---

## Database

### Initialization
The database is automatically created when the app starts:
1. SQLite database created at `Database/complaints.db`
2. Schema created from models
3. Sample data seeded (admin/user accounts with sample complaints)

### Reset Database
Delete `Database/complaints.db` and restart the app to create fresh database.

### View Database
Use VS Code SQLite extension:
1. Open Command Palette
2. Search "SQLite: Open Database"
3. Select `Database/complaints.db`

---

## Features Implementation

### Sentiment Analysis
Located in `routes/complaint.py` - `analyze_sentiment()` function:
- Checks for positive/negative keywords
- Returns: Positive, Negative, Urgent, or Neutral

### Live Search
API: `/api/search?q=<query>`
- Returns top 5 matching complaints
- Filters by user role (admins see all, users see their own)

### Export Reports
CSV export with fields:
- Ticket ID, Title, Description, Category, Priority, Status, Date, Customer

### Chart Analytics
Uses Chart.js for:
- Pie charts (category distribution)
- Bar charts (status distribution)
- Line charts (trend analysis)

---

## Testing

### Run Tests
```bash
python -m pytest test_routes.py -v
```

### Test Coverage
- Authentication (login)
- Route accessibility
- Session management
- Redirect handling

### Add More Tests
Edit `test_routes.py` to add:
- API endpoint tests
- Model validation tests
- Service function tests

```python
def test_new_feature(client):
    response = client.post('/api/endpoint', data={...})
    assert response.status_code == 200
```

---

## Deployment

### For Production:
1. Set `debug=False` in `app.py`
2. Use production WSGI server:
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 Backend.app:app
   ```

3. Use environment variables for secrets:
   ```python
   import os
   SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key')
   ```

4. Set up HTTPS/SSL certificates

5. Use production database (PostgreSQL recommended):
   ```python
   app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
   ```

---

## Common Tasks

### Add New Model
1. Create file in `Backend/models/`
2. Import in `Backend/app.py`
3. Add to `db.create_all()`

### Add New Route
1. Create blueprint in `Backend/routes/`
2. Import and register in `app.py`
3. Create corresponding template

### Add New Template
1. Create in `Frontend/templates/`
2. Extend base.html
3. Use Jinja2 templating

### Add New CSS
1. Add to `Frontend/static/css/`
2. Link in base.html `<head>`

### Add New JavaScript
1. Add to `Frontend/static/js/`
3. Include in template before `</body>`

---

## Troubleshooting

### Import Errors
Ensure `Backend` is in sys.path - already configured in `app.py`

### Database Errors
- Delete `complaints.db` to reset
- Check file permissions
- Verify SQLite3 is installed

### Port Already in Use
Change port in `app.py`:
```python
app.run(debug=True, port=5001)
```

### Template Not Found
Verify path in `route` matches `Frontend/templates/` structure

### Static Files Not Loading
Clear browser cache (Ctrl+Shift+Delete) or restart Flask

---

## Best Practices

1. **Models:** Always use relationships for foreign keys
2. **Routes:** Check session before processing
3. **Database:** Use transactions for multi-step operations
4. **Security:** Hash passwords, validate inputs
5. **Performance:** Index frequently queried columns
6. **Logging:** Add print/logging for debugging
7. **Testing:** Test critical paths
8. **Documentation:** Comment complex logic

---

## Resources

- Flask: https://flask.palletsprojects.com/
- SQLAlchemy: https://docs.sqlalchemy.org/
- Bootstrap 5: https://getbootstrap.com/docs/5.0/
- Chart.js: https://www.chartjs.org/docs/latest/
- Werkzeug Security: https://werkzeug.palletsprojects.com/en/2.0.x/utils/

---

**Happy Coding!** 🚀

