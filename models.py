from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
db = SQLAlchemy()

class Story(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    summary = db.Column(db.String(500))
    category = db.Column(db.String(50))
    image_url = db.Column(db.String(500), default='')  # <-- YANGI: har bir hikoyada rasm
    date = db.Column(db.Date, default=datetime.utcnow)
    publish_at = db.Column(db.DateTime, nullable=True)
    is_published = db.Column(db.Boolean, default=False)
    views = db.Column(db.Integer, default=0)
    author_name = db.Column(db.String(100), nullable=True)
    is_user_submitted = db.Column(db.Boolean, default=False)

class Submission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    content = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(500), default='')  # <-- YANGI
    author_name = db.Column(db.String(100))
    telegram_username = db.Column(db.String(100))
    telegram_id = db.Column(db.String(50))
    status = db.Column(db.String(20), default='Kutilmoqda')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    admin_comment = db.Column(db.Text, nullable=True)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
