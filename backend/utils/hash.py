import hashlib
from schemas.enquiry import EmailRequest

def compute_enquiry_hash(email: EmailRequest):
    data = email.email_content + ''.join(p.product_name for p in email.products)
    return hashlib.sha256(data.encode()).hexdigest()
