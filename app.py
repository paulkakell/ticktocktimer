import os
from datetime import datetime
from flask import Flask, render_template, redirect, url_for, request, flash, session, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from dateutil.relativedelta import relativedelta
from urllib.parse import urlparse

# Load env variables
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///ticktoctimer.db')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default_secret')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

# Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    api_key = db.Column(db.String(64), unique=True, nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

    timers = db.relationship('Timer', backref='user', cascade='all, delete-orphan')

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Timer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    timer_type = db.Column(db.String(20), nullable=False)  # 'datetime' or 'duration'
    target_datetime = db.Column(db.DateTime, nullable=False)
    original_duration = db.Column(db.Integer, nullable=False)  # in seconds
    webhook_url = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Create admin user if not exists
@app.before_first_request
def create_tables():
    db.create_all()
    admin_username = os.getenv('ADMIN_USERNAME', 'admin')
    admin_password = os.getenv('ADMIN_PASSWORD', 'admin')
    admin = User.query.filter_by(username=admin_username).first()
    if not admin:
        admin = User(
            username=admin_username,
            password_hash=generate_password_hash(admin_password),
            api_key=os.urandom(32).hex(),
            is_admin=True
        )
        db.session.add(admin)
        db.session.commit()

# Utility to calculate remaining time
def get_time_remaining(timer):
    now = datetime.utcnow()
    if timer.target_datetime < now:
        return None
    rd = relativedelta(timer.target_datetime, now)
    return {
        'years': rd.years,
        'months': rd.months,
        'days': rd.days,
        'hours': rd.hours,
        'minutes': rd.minutes,
        'seconds': rd.seconds
    }

# Routes

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if not user or not user.check_password(password) or not user.is_admin:
            flash('Invalid credentials', 'danger')
            return redirect(url_for('login'))
        login_user(user)
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/admin')
@login_required
def dashboard():
    if not current_user.is_admin:
        abort(403)
    users = User.query.all()
    return render_template('users.html', users=users)

@app.route('/admin/users/create', methods=['GET', 'POST'])
@login_required
def create_user():
    if not current_user.is_admin:
        abort(403)
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'danger')
            return redirect(url_for('create_user'))
        user = User(
            username=username,
            password_hash=generate_password_hash(password),
            api_key=os.urandom(32).hex(),
            is_admin=False
        )
        db.session.add(user)
        db.session.commit()
        flash('User created', 'success')
        return redirect(url_for('dashboard'))
    return render_template('create_user.html')

@app.route('/admin/users/delete/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    if not current_user.is_admin:
        abort(403)
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash('User deleted', 'success')
    return redirect(url_for('dashboard'))

@app.route('/admin/timers')
@login_required
def list_timers():
    if not current_user.is_admin:
        abort(403)
    timers = Timer.query.all()
    return render_template('timers.html', timers=timers)

@app.route('/admin/timers/create', methods=['GET', 'POST'])
@login_required
def create_timer():
    if not current_user.is_admin:
        abort(403)
    users = User.query.filter_by(is_admin=False).all()
    if request.method == 'POST':
        name = request.form['name']
        timer_type = request.form['timer_type']
        user_id = int(request.form['user_id'])
        webhook_url = request.form['webhook_url'] or None
        if timer_type == 'datetime':
            target_str = request.form['target_datetime']
            target_dt = datetime.fromisoformat(target_str)
            original_duration = int((target_dt - datetime.utcnow()).total_seconds())
        else:  # duration
            years = int(request.form.get('years', 0))
            months = int(request.form.get('months', 0))
            days = int(request.form.get('days', 0))
            hours = int(request.form.get('hours', 0))
            minutes = int(request.form.get('minutes', 0))
            seconds = int(request.form.get('seconds', 0))
            rd = relativedelta(years=years, months=months, days=days,
                               hours=hours, minutes=minutes, seconds=seconds)
            target_dt = datetime.utcnow() + rd
            original_duration = int(rd.years*365*24*3600 + rd.months*30*24*3600 + rd.days*24*3600 +
                                     rd.hours*3600 + rd.minutes*60 + rd.seconds)
        timer = Timer(
            name=name,
            timer_type=timer_type,
            target_datetime=target_dt,
            original_duration=original_duration,
            webhook_url=webhook_url,
            user_id=user_id
        )
        db.session.add(timer)
        db.session.commit()
        flash('Timer created', 'success')
        return redirect(url_for('list_timers'))
    return render_template('create_timer.html', users=users)

@app.route('/admin/timers/delete/<int:timer_id>', methods=['POST'])
@login_required
def delete_timer(timer_id):
    if not current_user.is_admin:
        abort(403)
    timer = Timer.query.get_or_404(timer_id)
    db.session.delete(timer)
    db.session.commit()
    flash('Timer deleted', 'success')
    return redirect(url_for('list_timers'))

# API endpoints

def authenticate_api(request):
    api_key = request.headers.get('X-API-KEY')
    if not api_key:
        return None
    return User.query.filter_by(api_key=api_key).first()

@app.route('/api/timers/<int:timer_id>', methods=['GET'])
def api_get_timer(timer_id):
    user = authenticate_api(request)
    if not user:
        return jsonify({'error': 'Unauthorized'}), 401
    timer = Timer.query.get_or_404(timer_id)
    if timer.user_id != user.id:
        return jsonify({'error': 'Forbidden'}), 403
    remaining = get_time_remaining(timer)
    if remaining is None:
        return jsonify({'message': 'Timer expired'}), 200
    return jsonify(remaining), 200

@app.route('/api/timers/<int:timer_id>/reset', methods=['POST'])
def api_reset_timer(timer_id):
    user = authenticate_api(request)
    if not user:
        return jsonify({'error': 'Unauthorized'}), 401
    timer = Timer.query.get_or_404(timer_id)
    if timer.user_id != user.id:
        return jsonify({'error': 'Forbidden'}), 403
    # Reset logic: set new target based on original_duration
    timer.created_at = datetime.utcnow()
    timer.target_datetime = datetime.utcnow() + relativedelta(seconds=timer.original_duration)
    db.session.commit()
    return jsonify({'message': 'Timer reset'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
