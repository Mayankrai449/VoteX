from datetime import datetime, date


def calculate_age(dob: date) -> int:
    today = datetime.today().date()
    age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
    return age