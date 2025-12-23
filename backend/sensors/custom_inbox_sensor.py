from airflow.sensors.python import PythonSensor
from scripts.email_parsing import fetch_latest_email_by_subject

def check_unseen_emails(**kwargs):
    """Check for unseen emails with subject 'Requirement'"""
    email_text, _, _, _ = fetch_latest_email_by_subject("Requirement UNSEEN")
    return bool(email_text)  # True if an unseen email is found

class CustomInboxSensor(PythonSensor):
    """Custom sensor to monitor inbox for new emails with subject 'Requirement'"""
    def __init__(self, **kwargs):
        # Remove poke_interval, timeout, and soft_fail from kwargs to avoid duplication
        sensor_kwargs = {k: v for k, v in kwargs.items() if k not in ['poke_interval', 'timeout', 'soft_fail']}
        super().__init__(
            python_callable=check_unseen_emails,
            poke_interval=60,
            timeout=3600,
            soft_fail=False,
            **sensor_kwargs
        )