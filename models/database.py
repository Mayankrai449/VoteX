from pymongo import MongoClient

def get_database_connection():
    conn = MongoClient("mongodb+srv://Mayankrai449:RWHLI4g2RqoHljpQ@cluster0.7hu8wbd.mongodb.net/votingsys")
    return conn.votingsys
