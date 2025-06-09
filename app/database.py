from . import db
from flask_sqlalchemy import SQLAlchemy
from flask import current_app
import os

def init_db():
    if not os.path.exists(current_app.config['SQLALCHEMY_DATABASE_URI']):
        db.create_all()
    else:
        print("Database already exists!")

def get_db():
    return db.session

def close_db():
    db.session.remove()
