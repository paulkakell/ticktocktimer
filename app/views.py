from flask import render_template, request, redirect, url_for
from . import app, db
from .models import Timer, User
from flask_login import current_user

@app.route('/')
def index():
    timers = Timer.query.all()
    return render_template('index.html', timers=timers)

@app.route('/admin')
def admin_dashboard():
    users = User.query.all()
    return render_template('admin_dashboard.html', users=users)

@app.route('/timer/<int:timer_id>')
def view_timer(timer_id):
    timer = Timer.query.get(timer_id)
    if timer:
        return render_template('view_timer.html', timer=timer)
    return redirect(url_for('index'))
