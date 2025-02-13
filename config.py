import os

class Config:
    SECRET_KEY = "ma_cle_secrete"
    SQLALCHEMY_DATABASE_URI = "postgresql://postgres:komi0101@localhost/employe"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
