import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'ma_cle_secrete')
    #SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'postgresql://postgres:komi0101@localhost/employe')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///local.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
