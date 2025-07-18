from datetime import datetime
import uuid

def generate_enquiry_id():
    now = datetime.utcnow()
    month = str(now.month).zfill(2)
    year = str(now.year)[-2:]
    random_num = str(uuid.uuid4().int)[:4].zfill(4)
    return f"isp{month}/{year}/{random_num}"
