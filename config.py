import os

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "mysql+pymysql://flaskuser:flask123@localhost/student_db"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
