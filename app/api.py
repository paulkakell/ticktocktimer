from flask import request, jsonify
from . import app
from .models import Timer, User
from datetime import datetime
import json

@app.route('/api/timers', methods=['GET'])
def get_timers():
    api_key = request.headers.get('API-Key')
    user = User.query.filter_by(api_key=api_key).first()
    
    if user:
        timers = Timer.query.filter_by(user_id=user.id).all()
        return jsonify([timer.serialize() for timer in timers])
    return jsonify({'error': 'Unauthorized'}), 401
