import os
import psycopg2

DATABASE_URL = os.getenv("DATABASE_URL")

try:
    conn = psycopg2.connect(DATABASE_URL)
    print("Connexion réussie à PostgreSQL !")
    conn.close()
except Exception as e:
    print("Erreur de connexion :", e)
