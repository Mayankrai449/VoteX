from datetime import datetime, date
import base64

def encode_id(title: str, username: str) -> str:
    encoded_title = base64.urlsafe_b64encode(title.encode()).decode()
    encoded_username = base64.urlsafe_b64encode(username.encode()).decode()
    combined_str = f"{encoded_title}|{encoded_username}"
    return combined_str

def decode_id(encoded_id: str) -> tuple:
    try:
        encoded_title, encoded_username = encoded_id.split('|')
        title = base64.urlsafe_b64decode(encoded_title.encode()).decode()
        username = base64.urlsafe_b64decode(encoded_username.encode()).decode()
        return title, username
    except (ValueError, UnicodeDecodeError):
        return None, None

def calculate_age(dob: str) -> int:
    dob_date = datetime.strptime(dob, '%m/%d/%Y').date()
    today = datetime.today().date()
    
    age = today.year - dob_date.year - ((today.month, today.day) < (dob_date.month, dob_date.day))
    return age