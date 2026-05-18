from flask import Flask
from config import Config
import mysql.connector

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Simple database connection test helper
    try:
        db = mysql.connector.connect(
            host=app.config['DB_HOST'],
            user=app.config['DB_USER'],
            password=app.config['DB_PASSWORD'],
            database=app.config['DB_NAME']
        )
        print("MySQL Database connection successful!")
        db.close()
    except mysql.connector.Error as err:
        print(f"MySQL Connection Error: {err}")

    # Register routes
    with app.app_context():
        from . import routes
        
    return app