from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

class Timer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    target_date = db.Column(db.DateTime)
    duration = db.Column(db.Interval)
    expired = db.Column(db.Boolean, default=False)
    
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    api_key = db.Column(db.String(256), unique=True, nullable=False)
    timers = db.relationship('Timer', backref='user', lazy=True)
