import os

class Config:
    """
    LOCAL MYSQL (Development)
    - Uncomment the DB_* variables below to use local MySQL
    """
    # DB_HOST = "localhost"
    # DB_USER = "root"          
    # DB_PASSWORD = "passwordito"
    # DB_NAME = "saving_db"

    """
    SUPABASE POSTGRESQL (Production)
    - Uses environment variable DATABASE_URL
    - Set in .env file or Supabase dashboard
    """
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        'postgresql://postgres:[Nigga#69_$%^&]@db.jagjccudqpzrvrbsgfvr.supabase.co:5432/postgres'
    )
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False  # Set to True for SQL debugging