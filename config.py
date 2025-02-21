import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'ma_cle_secrete')
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        #'postgresql://gestion_decompte_db_user:pDRTgJMAdeR3zCQLmB3uGg8FlW1MHMc0@dpg-curkk9in91rc73ctafs0-a/gestion_decompte_db'
        'postgresql://postgres:komi0101@localhost/employe'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
