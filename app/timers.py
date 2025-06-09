from . import db
from datetime import datetime, timedelta
from sqlalchemy.ext.hybrid import hybrid_property

class Timer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    target_date = db.Column(db.DateTime, nullable=True)
    duration = db.Column(db.Interval, nullable=True)
    expired = db.Column(db.Boolean, default=False)

    @hybrid_property
    def time_left(self):
        if self.target_date:
            return self.target_date - datetime.utcnow()
        elif self.duration:
            elapsed_time = datetime.utcnow() - self.created_at
            return self.duration - elapsed_time
        return None

    def reset(self):
        if self.target_date:
            self.target_date = datetime.utcnow() + self.time_left
        elif self.duration:
            self.duration = timedelta(days=0)

    def __repr__(self):
        return f'<Timer {self.name}>'

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    api_key = db.Column(db.String(256), unique=True, nullable=False)
    timers = db.relationship('Timer', backref='user', lazy=True)

    def __repr__(self):
        return f'<User {self.username}>'
