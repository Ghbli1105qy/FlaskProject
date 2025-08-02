from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import UserMixin
import bcrypt

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

    def set_password(self, password):
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))

class Devices(db.Model):
    id = db.Column(db.String(50), primary_key=True)
    ip_address = db.Column(db.String(50), nullable=False)
    port = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class SensorData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.String(50), db.ForeignKey('device.id'), nullable=False)
    temperature = db.Column(db.Float)
    temperature_time = db.Column(db.DateTime)
    humidity = db.Column(db.Float)
    humidity_time = db.Column(db.DateTime)
    rainfall = db.Column(db.Float)
    rainfall_time = db.Column(db.DateTime)
    battery = db.Column(db.Float)
    upload_time = db.Column(db.DateTime, nullable=False)
    processed_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'device_id': self.device_id,
            'temperature': self.temperature,
            'humidity': self.humidity,
            'rainfall': self.rainfall,
            'battery': self.battery,
            'upload_time': self.upload_time.isoformat() if self.upload_time else None
        }