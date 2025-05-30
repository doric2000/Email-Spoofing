import requests

def read_benign_email(source: str, source_type: str) -> str:
    """Read a benign email from a file, URL, or string."""
    if source_type == 'file':
        with open(source, 'r', encoding='utf-8') as f:
            return f.read()
    elif source_type == 'url':
        response = requests.get(source)
        response.raise_for_status()
        return response.text
    elif source_type == 'string':
        return source
    else:
        raise ValueError("Invalid source_type. Must be 'file', 'url', or 'string'.")

def merge_benign_email(benign_email: str, data: dict) -> dict:
    """Merge benign email content with user data."""
    # Example: Extract subject and some content from the benign email
    lines = benign_email.splitlines()
    subject_line = next((line for line in lines if line.lower().startswith('subject:')), 'Subject: No Subject')
    data['subject'] = subject_line.split(':', 1)[1].strip() if ':' in subject_line else 'No Subject'

    # Optionally, extract additional content or placeholders from the benign email
    # For simplicity, we'll just append the benign email content to the data dictionary
    data['benign_content'] = benign_email
    return data
