from datetime import datetime
import pytz

IST = pytz.timezone("Asia/Kolkata")

def get_ist_date_str():
    """
    Returns today's date in IST as YYYY-MM-DD
    """
    return datetime.now(IST).date().isoformat()

print(get_ist_date_str())
