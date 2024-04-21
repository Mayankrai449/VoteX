from pymongo import MongoClient
from bson.codec_options import CodecOptions
from control import move_expired_poll_to_history

def register_event_handlers():
    conn = MongoClient("mongodb+srv://Mayankrai449:RWHLI4g2RqoHljpQ@cluster0.7hu8wbd.mongodb.net/votingsys")
    db = conn.votingsys

    try:
        db.command_runner.register_command("move_expired_poll_to_history", move_expired_poll_to_history)
    except Exception as e:
        print(f"Error registering event handler: {e}")

register_event_handlers()