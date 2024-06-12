from pymongo import MongoClient
import os
db_url = os.getenv("DATABASE_URL")

def get_database_connection():
    conn = MongoClient(db_url)
    return conn.votingsys
