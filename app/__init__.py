from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize SQLAlchemy
    db.init_app(app)

    # Test database connection
    with app.app_context():
        try:
            db.session.execute('SELECT 1')
            print("✓ Supabase PostgreSQL connection successful!")
        except Exception as err:
            print(f"✗ Database Connection Error: {err}")

    # Register routes
    with app.app_context():
        from . import routes
        
    return app