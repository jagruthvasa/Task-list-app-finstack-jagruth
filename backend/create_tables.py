from flask import Flask
from config import Config
from models import db

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

with app.app_context():
    try:
        db.create_all()
        print("Tables created successfully")
    except Exception as e:
        print(f"Error creating tables: {e}")
