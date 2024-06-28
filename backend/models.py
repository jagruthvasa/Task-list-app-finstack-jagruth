from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Task(db.Model):
    __tablename__ = 'tasks'
    id = db.Column(db.Integer, primary_key=True)
    entity_name = db.Column(db.String(100), nullable=False)
    date_created = db.Column(db.Integer, nullable=False)
    task_time = db.Column(db.Integer, nullable=False)
    phone_number = db.Column(db.String(10), nullable=False)
    task_type = db.Column(db.String(50), nullable=False)
    contact_person = db.Column(db.String(100), nullable=False)
    note = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(10), default='Open', nullable=False)
