import os

class Config:
    SECRET_KEY = 'be42c20aec2a34d0fec9daab0a04c43f'
    file_path = os.path.abspath(os.getcwd())+"\site.db"
    SQLALCHEMY_DATABASE_URI = 'sqlite:///'+file_path
    MAIL_SERVER='smtp.gmail.com'
    MAIL_PORT = 465
    MAIL_USERNAME = ''
    MAIL_PASSWORD = ''
    MAIL_USE_TLS= False
    MAIL_USE_SSL = True
    MAX_CONTENT_LENGTH = 16*1024*1024
    SCHEDULER_API_ENABLED = True