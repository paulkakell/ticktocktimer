from flask import render_template, redirect, url_for
from . import app, db
from .models import Timer
from flask_login import current_user

@app.route('/')
def index():
    return render_template('index.html', timers=Timer.query.all())
