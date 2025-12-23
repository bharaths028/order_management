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
from crud.customer import get_customer_by_email, create_customer, get_customer
from schemas.customer import CustomerCreate
from schemas.enquiry import EnquiryCreate, EnquiryProductBase
import uuid
import boto3

# Email account credentials
EMAIL = "test@ispstandards.com"
PASSWORD = "uhix jhvx lozd ebou"
IMAP_SERVER = "imap.gmail.com"
SUBJECT_FILTER = "Requirement"

# AWS credentials and configuration
AWS_ACCESS_KEY_ID = ""
AWS_SECRET_ACCESS_KEY = ""
AWS_REGION = ""

# Initialize Bedrock client
bedrock_client = boto3.client(
    'bedrock-runtime',
    region_name=AWS_REGION,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY
)

# FastAPI endpoint for creating enquiries
API_BASE_URL = "https://order-management-api-knhi.onrender.com/v1/enquiries/"

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
        status, data = mail.search(None, f'(SUBJECT "{subject_filter}")')
        if status != "OK" or not data[0]:
            print(f"No emails found with subject containing '{subject_filter}'.")
            return None, None
        email_ids = data[0].split()
        latest_email = None
        latest_date = None
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
        if latest_email:
            sender = latest_email.get("From", "Unknown")
            email_content = f"**From:** {sender}\n**Date:** {latest_date.strftime('%Y-%m-%d %H:%M:%S %z')}\n"
            if latest_email.is_multipart():
                for part in latest_email.walk():
                    if part.get_content_type() == "text/plain":
                        email_content += part.get_payload(decode=True).decode("utf-8", errors="ignore") + "\n"
            else:
                email_content += latest_email.get_payload(decode=True).decode("utf-8", errors="ignore") + "\n"
            return email_content, latest_date
    except Exception as e:
        print(f"Error fetching email: {e}")
        return None, None
    finally:
        mail.logout()

# Extract details using Bedrock API
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
Ensure all products listed in the email are included, even if some fields are missing (use null for missing fields). Set "flag" to "y" if the product is identified, "n" if unknown. Use the email date for "enquiry_date" and "enquiry_time". Include any additional requirements (e.g., packaging, standards) in "variant" or "standards" if applicable.
Email content:
{email_text}
"""
    
    try:
        print(f"Prompt length: {len(prompt)} characters")
        
        # Call Bedrock Converse API
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
                "maxTokens": 2048
            }
        )
        
        print("Received response from Bedrock API")
        print(f"Response keys: {response.keys()}")
        
        # Extract the text from the response
        # Bedrock Converse API returns output.message.content
        if 'output' not in response:
            print("ERROR: No output in response")
            print(f"Full response: {json.dumps(response, indent=2, default=str)}")
            return None
        
        if 'message' not in response['output']:
            print("ERROR: No message in output")
            return None
        
        message = response['output']['message']
        if 'content' not in message or not message['content']:
            print("ERROR: No content in message")
            return None
        
        generated_text = message['content'][0]['text']
        print(f"Generated text length: {len(generated_text)}")
        print("Generated text:", generated_text[:500] + "..." if len(generated_text) > 500 else generated_text)
        
        # Try to extract JSON from the response
        json_match = re.search(r'```json\s*([\s\S]*?)\s*```', generated_text, re.DOTALL)
        if not json_match:
            json_match = re.search(r'```\s*([\s\S]*?)\s*```', generated_text, re.DOTALL)
        
        if not json_match:
            # Try to parse the whole text as JSON
            potential_json = generated_text.strip()
            try:
                extracted_data = json.loads(potential_json)
                print("Parsed JSON from full text")
                return extracted_data
            except json.JSONDecodeError:
                print("No valid JSON found in full text")
                return None
        
        json_str = json_match.group(1).strip()
        print("Extracted JSON string:", json_str[:200] + "..." if len(json_str) > 200 else json_str)
        
        try:
            extracted_data = json.loads(json_str)
            print("Successfully parsed JSON from Bedrock response")
            return extracted_data
        except json.JSONDecodeError as e:
            print(f"Failed to parse JSON: {e}")
            return None
            
    except Exception as e:
        print(f"Bedrock API error: {e}")
        import traceback
        traceback.print_exc()
        return None
        print(f"Error: {response.status_code} - {response.text}")
        return None

# Get or create customer
def get_or_create_customer(db: Session, customer_details: dict):
    email = customer_details.get("email")
    print("Customer email:", email)
    if not email:
        raise ValueError("Customer email is required")
    existing_customer = get_customer_by_email(db, email)
    if existing_customer:
        print(f"Found existing customer with email {email}: customer_id={existing_customer.customer_id}")
        # Verify customer exists in database
        customer_check = get_customer(db, existing_customer.customer_id)
        if not customer_check:
            print(f"Error: Customer with ID {existing_customer.customer_id} not found in database")
        return existing_customer.customer_id
    print(f"No existing customer found with email {email}, creating new customer")
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
    db.commit()  # Ensure customer is committed
    print(f"Created new customer with email {email}: customer_id={new_customer.customer_id}")
    # Verify new customer exists
    customer_check = get_customer(db, new_customer.customer_id)
    if not customer_check:
        print(f"Error: Newly created customer with ID {new_customer.customer_id} not found in database")
    return new_customer.customer_id

# Post enquiry to FastAPI endpoint
def post_enquiry_to_api(enquiry_data: EnquiryCreate):
    headers = {
        "Content-Type": "application/json",
        "accept": "application/json"
    }
    # Convert UUID to string in the payload
    payload = enquiry_data.dict()
    payload['customer_id'] = str(payload['customer_id'])
    print("Payload to be sent:", json.dumps(payload, indent=2))
    try:
        response = requests.post(API_BASE_URL, headers=headers, json=payload)
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

# Main execution
if __name__ == "__main__":
    print(f"Fetching the latest email with subject containing '{SUBJECT_FILTER}'...")
    email_text, email_date = fetch_latest_email_by_subject(SUBJECT_FILTER)
    if email_text and email_date:
        print("Extracting details with Gemini API...")
        extracted_data = extract_details_with_gemini(email_text, email_date)
        if extracted_data:
            print("Extracted data:", json.dumps(extracted_data, indent=2))
            db = next(get_db())
            try:
                # Handle customer
                customer_details = extracted_data["customer_details"]
                customer_id = get_or_create_customer(db, customer_details)
                
                # Prepare enquiry
                enquiry_details = extracted_data["enquiry_details"]
                products = [
                    EnquiryProductBase(
                        quantity=float(product["quantity"]) if product["quantity"] is not None else 0.0,
                        chemical_name=product["chemical_name"][:100],
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
                
                # Post to API within the same session
                print("Posting enquiry to API...")
                result = post_enquiry_to_api(enquiry)
                if result:
                    print(f"Enquiry created: {json.dumps(result, indent=2)}")
                else:
                    print("Failed to create enquiry")
            except Exception as e:
                print(f"Error processing enquiry: {e}")
            finally:
                db.close()
        else:
            print("Failed to extract data from email.")
    else:
        print("No email fetched.")