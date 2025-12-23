import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import imaplib
import email
from datetime import datetime
import requests
import json
import re
from sqlalchemy.orm import Session
from fastapi import HTTPException
from dependencies.database import get_db
from models.customer import Customer
from crud.customer import get_customer_by_email, create_customer, get_customer
from schemas.customer import CustomerCreate
from schemas.enquiry import EnquiryCreate, EnquiryProductBase
import uuid
from airflow.models import Variable
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import smtplib
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr
import boto3

# Fetch credentials from Airflow Variables
EMAIL = Variable.get("EMAIL", default_var="test@ispstandards.com")
PASSWORD = Variable.get("EMAIL_PASSWORD", default_var="uhix jhvx lozd ebou")
IMAP_SERVER = "imap.gmail.com"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SUBJECT_FILTER = "Requirement"

# Gemini API key from Airflow Variable
api_key = Variable.get("GEMINI_API_KEY", default_var="AIzaSyCn1WRZZN_qXybN1b_Wixeq--V5qtY-xBE")
if not api_key or api_key.strip() == "":
    raise ValueError("GEMINI_API_KEY is not set or is empty in Airflow Variables")

# FastAPI endpoint and base URL for enquiries
API_BASE_URL = Variable.get("API_BASE_URL", default_var="http://fastapi:8000/v1")
ENQUIRY_BASE_URL = Variable.get("ENQUIRY_BASE_URL", default_var="https://dapper-tapioca-4bf95f.netlify.app")

# Fetch AWS credentials from Airflow Variables
AWS_ACCESS_KEY_ID = Variable.get("AWS_ACCESS_KEY_ID", default_var="")
AWS_SECRET_ACCESS_KEY = Variable.get("AWS_SECRET_ACCESS_KEY", default_var="")
AWS_REGION = Variable.get("AWS_REGION", default_var="")

# Initialize Bedrock client with explicit credentials
bedrock_client = boto3.client(
    'bedrock-runtime',
    region_name=AWS_REGION,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY
)

# Custom JSON encoder to handle UUID
class UUIDEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, uuid.UUID):
            return str(obj)
        return super().default(obj)

# Fetch the latest email with the specified subject filter
def fetch_latest_email_by_subject(subject_filter):
    mail = imaplib.IMAP4_SSL(IMAP_SERVER)
    try:
        mail.login(EMAIL, PASSWORD)
        mail.select("inbox")
        search_criteria = f'UNSEEN SUBJECT "{SUBJECT_FILTER}"' if "UNSEEN" in subject_filter else f'SUBJECT "{SUBJECT_FILTER}"'
        status, data = mail.search(None, search_criteria)
        if status != "OK" or not data[0]:
            print(f"No emails found with criteria '{search_criteria}'.")
            return None, None, None, None
        email_ids = data[0].split()
        latest_email = None
        latest_date = None
        latest_email_id = None
        sender = None
        cc_recipients = []
        for email_id in email_ids:
            status, msg_data = mail.fetch(email_id, "(RFC822)")
            raw_email = msg_data[0][1]
            msg = email.message_from_bytes(raw_email)
            date_str = msg.get("Date", "Unknown")
            try:
                email_date = datetime.strptime(date_str.split(" (")[0], "%a, %d %b %Y %H:%M:%S %z")
            except (ValueError, TypeError):
                email_date = datetime(1970, 1, 1)
            if latest_date is None or email_date > latest_date:
                latest_date = email_date
                latest_email = msg
                latest_email_id = email_id
                sender = parseaddr(msg.get("From", ""))[1]
                cc_header = msg.get("CC", "")
                if cc_header:
                    cc_recipients = [parseaddr(addr)[1] for addr in cc_header.split(",") if parseaddr(addr)[1]]
        if latest_email:
            email_content = f"**From:** {sender}\n**Date:** {latest_date.strftime('%Y-%m-%d %H:%M:%S %z')}\n"
            if latest_email.is_multipart():
                for part in latest_email.walk():
                    if part.get_content_type() == "text/plain":
                        email_content += part.get_payload(decode=True).decode("utf-8", errors="ignore") + "\n"
            else:
                email_content += latest_email.get_payload(decode=True).decode("utf-8", errors="ignore") + "\n"
            if latest_email_id:
                mail.store(latest_email_id, '+FLAGS', '\\Seen')
            return email_content, latest_date, sender, cc_recipients
    except Exception as e:
        print(f"Error fetching email: {e}")
        return None, None, None, None
    finally:
        mail.logout()

# Extract details using Gemini API
def extract_details_with_gemini(email_text, email_date):
    print("Sending request to Bedrock API...")
    max_email_length = 10000
    if len(email_text) > max_email_length:
        print(f"Email content too long ({len(email_text)} chars), truncating to {max_email_length} chars")
        email_text = email_text[:max_email_length] + "... [truncated]"
    
    prompt = f"""
Extract the customer details and enquiry details from the following email and format the response as a JSON object with the following structure:
{{
  "customer_details": {{
    "customer_name": "",
    "email": "",
    "phone": "",
    "company_name": null,
    "address": null
  }},
  "enquiry_details": {{
    "enquiry_date": "{email_date.strftime('%Y-%m-%d')}",
    "enquiry_time": "{email_date.strftime('%H:%M')}",
    "products": [
      {{
        "quantity": 0.0,
        "chemical_name": null,
        "cas_number": null,
        "cat_number": null,
        "molecular_weight": null,
        "variant": null,
        "standards": null,
        "flag": "y",
        "attachment_ref": null
      }}
    ]
  }}
}}
IMPORTANT: Return ONLY valid JSON. Ensure all null values are written as null (not n). Do not include any markdown, code blocks, or explanatory text - just the raw JSON object.
Ensure all products listed in the email are included, even if some fields are missing (use null for missing fields). Set "flag" to "y" if the product is identified, "n" if unknown. Use the email date for "enquiry_date" and "enquiry_time". Include any additional requirements (e.g., packaging, standards) in "variant" or "standards" if applicable.
Email content:
{email_text}
"""
    print(f"Prompt length: {len(prompt)} characters")
    
    try:
        # Use the newer Converse API
        response = bedrock_client.converse(
            modelId="anthropic.claude-3-sonnet-20240229-v1:0",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "text": prompt
                        }
                    ]
                }
            ],
            inferenceConfig={
                "maxTokens": 4096
            }
        )
        
        print("Received response from Bedrock API")
        
        # Extract the text from Bedrock Converse API response
        # Response structure: response['output']['message']['content'][0]['text']
        if 'output' not in response or 'message' not in response['output']:
            print("ERROR: Unexpected response structure")
            return None
        
        message = response['output']['message']
        if 'content' not in message or not message['content']:
            print("ERROR: No content in message")
            return None
        
        generated_text = message['content'][0]['text']
        print("Generated text length:", len(generated_text))
        print("First 500 chars of response:", generated_text[:500])
        
        # Try to extract JSON with multiple patterns
        json_match = re.search(r'```json\s*([\s\S]*?)\s*```', generated_text, re.DOTALL)
        if not json_match:
            json_match = re.search(r'```\s*([\s\S]*?)\s*```', generated_text, re.DOTALL)
        
        if json_match:
            json_str = json_match.group(1).strip()
            print("Extracted JSON from code block")
        else:
            # Try to find JSON object directly (starts with { and ends with })
            json_start = generated_text.find('{')
            json_end = generated_text.rfind('}')
            if json_start != -1 and json_end != -1 and json_end > json_start:
                json_str = generated_text[json_start:json_end+1].strip()
                print("Extracted JSON from text (no code block)")
            else:
                print("Could not find JSON in response")
                print("Full response:", generated_text)
                return None
        
        print("JSON string that will be parsed (first 300 chars):", json_str[:300])
        
        # Try to fix common JSON issues
        # Fix incomplete null values like "standards": n with "standards": null
        json_str = re.sub(r':\s*n(?![a-zA-Z_])', ': null', json_str)
        # Fix incomplete null values like "standards": tru with "standards": true
        json_str = re.sub(r':\s*tru(?![a-zA-Z_])', ': true', json_str)
        # Fix incomplete false values like "standards": fal with "standards": false
        json_str = re.sub(r':\s*fal(?![a-zA-Z_])', ': false', json_str)
        
        try:
            extracted_data = json.loads(json_str)
            print("Parsed JSON data successfully")
            return extracted_data
        except json.JSONDecodeError as e:
            print(f"Failed to parse JSON: {e}")
            print(f"JSON string that failed to parse: {json_str[:500]}")
            # Try one more time - find the last complete closing brace
            last_brace = json_str.rfind('}')
            if last_brace > 0:
                json_str_truncated = json_str[:last_brace+1]
                try:
                    extracted_data = json.loads(json_str_truncated)
                    print("Parsed JSON data successfully after truncation")
                    return extracted_data
                except json.JSONDecodeError:
                    print("Failed to parse even after truncation")
                    return None
            return None
            
    except Exception as e:
        print(f"Bedrock API error: {e}")
        import traceback
        traceback.print_exc()
        return None

# Send acknowledgment email
def send_acknowledgment_email(sender, cc_recipients, enquiry_data, customer_details):
    try:
        enquiry_id = enquiry_data.get("enquiry_id", "N/A")
        enquiry_name = f"Enquiry from {customer_details.get('customer_name', 'Unknown')} on {enquiry_data.get('enquiry_date', 'N/A')}"
        customer_name = customer_details.get("customer_name", "Unknown")
        company_name = customer_details.get("company_name", "N/A")
        date_time = f"{enquiry_data.get('enquiry_date', 'N/A')} {enquiry_data.get('enquiry_time', 'N/A')}"
        edit_url = f"{ENQUIRY_BASE_URL}/enquiries/{enquiry_id}"

        subject = f"Acknowledgment: Enquiry {enquiry_id}"
        body = f"""
Dear {customer_name},

Thank you for your enquiry. We have received your request and it is being processed. Below are the details:

- Enquiry ID: {enquiry_id}
- Enquiry Name: {enquiry_name}
- Customer Name: {customer_name}
- Company Name: {company_name}
- Date & Time: {date_time}
- Edit Enquiry: {edit_url}

We will get back to you soon with further details.

Best regards,
ISP Standards Team
"""
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = formataddr(("ISP Standards", EMAIL))
        msg["To"] = sender
        if cc_recipients:
            msg["Cc"] = ", ".join(cc_recipients)

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL, PASSWORD)
            server.sendmail(EMAIL, [sender] + cc_recipients, msg.as_string())
        print(f"Acknowledgment email sent to {sender} with CC: {cc_recipients}")
    except Exception as e:
        print(f"Error sending acknowledgment email: {e}")
        raise

# Get or create customer
def get_or_create_customer(db: Session, customer_details: dict):
    email = customer_details.get("email")
    if not email:
        raise ValueError("Customer email is required")
    existing_customer = get_customer_by_email(db, email)
    if existing_customer:
        print(f"Found existing customer with email {email}: customer_id={existing_customer.customer_id}")
        customer_check = get_customer(db, existing_customer.customer_id)
        if not customer_check:
            print(f"Error: Customer with ID {existing_customer.customer_id} not found in database")
        return existing_customer.customer_id
    customer = CustomerCreate(
        customer_name=customer_details.get("customer_name", "Unknown"),
        company_name=customer_details.get("company_name", "Unknown"),
        email=email,
        phone=str(customer_details.get("phone")) if customer_details.get("phone") is not None else None,
        address=customer_details.get("address"),
        mobile=None,
        landline=None,
        department=None,
        title=None,
        tag=None,
        flag="y",
        contact_owner="ISP Email"
    )
    new_customer = create_customer(db, customer)
    db.flush()  # Flush to get the ID without committing the transaction
    customer_id = new_customer.customer_id
    print(f"Created new customer with email {email}: customer_id={customer_id}")
    db.commit()  # Now commit
    print(f"Customer committed to database: customer_id={customer_id}")
    # Verify customer was created by querying in a fresh session
    from dependencies.database import SessionLocal
    verify_db = SessionLocal()
    try:
        customer_check = verify_db.query(Customer).filter(Customer.customer_id == customer_id).first()
        if customer_check:
            print(f"Verified: Customer {customer_id} exists in database")
        else:
            print(f"Error: Newly created customer with ID {customer_id} not found in database!")
            raise ValueError(f"Customer {customer_id} was not persisted to database")
    finally:
        verify_db.close()
    return customer_id

# Post enquiry to FastAPI endpoint
def post_enquiry_to_api(enquiry_data: EnquiryCreate):
    headers = {
        "Content-Type": "application/json",
        "accept": "application/json"
    }
    payload = enquiry_data.dict()
    payload['customer_id'] = str(payload['customer_id'])
    print("Payload to be sent:", json.dumps(payload, indent=2))
    try:
        response = requests.post(f"{API_BASE_URL}/enquiries/", headers=headers, json=payload)
        if response.status_code == 201:
            print("Enquiry created successfully")
            return response.json()
        else:
            print(f"Failed to create enquiry: {response.status_code} - {response.text}")
            return None
    except requests.exceptions.ConnectionError:
        print(f"Connection error: Could not reach {API_BASE_URL}. Is the API server running?")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
        return None

# Main function for Airflow DAG
def parse_latest_requirement_email(**kwargs):
    print(f"Fetching the latest email with subject containing '{SUBJECT_FILTER}'...")
    email_text, email_date, sender, cc_recipients = fetch_latest_email_by_subject(SUBJECT_FILTER)
    if email_text and email_date and sender:
        print("Extracting details with Gemini API...")
        extracted_data = extract_details_with_gemini(email_text, email_date)
        if extracted_data:
            print("Extracted data:", json.dumps(extracted_data, indent=2))
            db = next(get_db())
            try:
                customer_details = extracted_data["customer_details"]
                customer_id = get_or_create_customer(db, customer_details)
                # Close the database session BEFORE making API calls to ensure all changes are flushed
                db.close()
                db = None
                
                # Give the database a moment to ensure replication/visibility
                import time
                time.sleep(1)
                
                enquiry_details = extracted_data["enquiry_details"]
                products = [
                    EnquiryProductBase(
                        quantity=float(product["quantity"]) if product["quantity"] is not None else 0.0,
                        chemical_name=product["chemical_name"],
                        cas_number=product["cas_number"],
                        cat_number=product["cat_number"],
                        molecular_weight=float(product["molecular_weight"]) if product["molecular_weight"] is not None else None,
                        variant=product["variant"],
                        standards="USA" if product["standards"] is None else product["standards"] if product["standards"] in {"USA", "UK"} else "USA",
                        flag=product["flag"],
                        attachment_ref=product["attachment_ref"]
                    )
                    for product in enquiry_details["products"]
                ]
                enquiry = EnquiryCreate(
                    customer_id=customer_id,
                    enquiry_date=enquiry_details["enquiry_date"],
                    enquiry_time=enquiry_details["enquiry_time"],
                    status="open",
                    is_enquiry_active=True,
                    enquiry_channel="Email",
                    products=products
                )
                
                print("Posting enquiry to API...")
                result = post_enquiry_to_api(enquiry)
                if result:
                    print(f"Enquiry created: {json.dumps(result, indent=2)}")
                    send_acknowledgment_email(sender, cc_recipients, result, customer_details)
                else:
                    print("Failed to create enquiry")
                    raise ValueError("Failed to create enquiry")
            except Exception as e:
                print(f"Error processing enquiry: {e}")
                raise
            finally:
                if db:
                    db.close()
        else:
            print("Failed to extract data from email.")
            raise ValueError("No data extracted from email")
    else:
        print("No email fetched or sender not found.")
        raise ValueError("No email found matching subject filter or missing sender")

if __name__ == "__main__":
    parse_latest_requirement_email()