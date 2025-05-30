#!/usr/bin/env python3
# phishing_step1_smart.py
# Compose a highly credible phishing email with dynamic family content

from email.message import EmailMessage
import requests

# Embedded Gmail-like HTML template with placeholders
TEMPLATE_HTML = '''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>{{SUBJECT}}</title>
  <style>
    /* Inline CSS only for maximum compatibility */
    body { margin:0; padding:0; font-family: Arial, sans-serif; }
    .header { background-color: #004080; padding:20px; text-align:center; color: #fff; }
    .header img { width:100px; }
    .content { padding:20px; color:#333; line-height:1.6; }
    .button { display:inline-block; padding:12px 24px; background:#004080; color:#fff;
              text-decoration:none; border-radius:4px; }
    .footer { padding:20px; font-size:12px; color:#888; text-align:center; }
  </style>
</head>
<body>
  <table width="100%" cellpadding="0" cellspacing="0">
    <tr><td class="header">
      <h1>{{COMPANY_NAME}} Security Team</h1>
    </td></tr><tr><td class="content">
      <p>Hi {{HONORIFIC}} {{USERNAME}},</p>
      <p>We hope this message finds you well. As part of our commitment to protecting every {{ROLE}} account at {{COMPANY_NAME}}, we’re rolling out a quick security check for your account.</p>
      <p><a href="{{VERIFY_LINK}}" class="button">Secure My Account</a></p>
      <p>This request was initiated by your manager, {{BOSS_NAME}}, to ensure compliance with our latest security policies.</p>
      {{SPOUSE_NOTICE}}
      {{FAMILY_NOTICE}}
      <p>If you did not request this verification, simply ignore this email or contact our support team.</p>
    </td></tr><tr><td class="footer">
      <p>Thank you for helping us keep your account secure,<br>The {{COMPANY_NAME}} Security Team</p>
    </td></tr>
  </table>
</body>
</html>'''

def get_user_input():
    """Get target information from the user via stdin."""
    return {
        "honorific":       input("Enter honorific/title (Mr, Ms, Dr): ").strip(),
        "username":        input("Enter recipient's full name: ").strip(),
        "mail_service":    input("Enter mail service name (e.g. Gmail): ").strip(),
        "subject":         input("Enter email subject/title: ").strip(),
        "role":            input("Enter recipient's role (e.g. student, manager): ").strip(),
        "personal_status": input("Enter personal status (single/married/other): ").strip(),
        "kids_info":       input("Enter kids info (no kids or ages comma-separated): ").strip(),
    }

def fill_template(html: str, data: dict) -> str:
    """Replace placeholders with user data and dynamic family content."""
    placeholders = {
        '{{HONORIFIC}}':    data['honorific'],
        '{{USERNAME}}':     data['username'],
        '{{ROLE}}':         data['role'],
        '{{COMPANY_NAME}}': data['company_name'],
        '{{BOSS_NAME}}':    data['boss_name'],
        '{{SUBJECT}}':      data['subject'],
        '{{VERIFY_LINK}}':  f"https://secure-{data['company_name'].lower()}.com/verify?user={data['username'].replace(' ', '%20')}"
    }
    placeholders['{{SPOUSE_NOTICE}}'] = (
        '<p>Please ensure your spouse has updated their security settings too.</p>'
        if data['personal_status'].lower() == 'married' else ''
    )
    kids = [k.strip() for k in data['kids_info'].split(',') if k.strip().isdigit()]
    placeholders['{{FAMILY_NOTICE}}'] = (
        f"<p>Please review the safety settings on your family’s devices (children ages: {', '.join(kids)}) to keep everyone protected.</p>"
        if kids else ''
    )
    for ph, val in placeholders.items():
        html = html.replace(ph, val)
    return html

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

def merge_benign_email(benign_email: str, data: dict, source_type: str) -> dict:
    """Merge benign email content with user data based on source type."""
    if source_type == 'url':
        # Use the entire email template from the URL and inject the malicious link
        data['html_body'] = benign_email.replace(
            '</body>',
            f'<p><a href=\"https://secure-{data["company_name"].lower()}.com/verify?user={data["username"].replace(" ", "%20")}\">Verify your account</a></p></body>'
        )
    elif source_type == 'string':
        # Extract sender and subject to make the email more credible
        lines = benign_email.splitlines()
        subject_line = next((line for line in lines if line.lower().startswith('subject:')), 'Subject: No Subject')
        data['subject'] = subject_line.split(':', 1)[1].strip() if ':' in subject_line else 'No Subject'
        sender_line = next((line for line in lines if line.lower().startswith('from:')), 'From: Unknown Sender')
        data['sender'] = sender_line.split(':', 1)[1].strip() if ':' in sender_line else 'Unknown Sender'
    elif source_type == 'file':
        # Treat the file content similarly to a string
        lines = benign_email.splitlines()
        subject_line = next((line for line in lines if line.lower().startswith('subject:')), 'Subject: No Subject')
        data['subject'] = subject_line.split(':', 1)[1].strip() if ':' in subject_line else 'No Subject'
        sender_line = next((line for line in lines if line.lower().startswith('from:')), 'From: Unknown Sender')
        data['sender'] = sender_line.split(':', 1)[1].strip() if ':' in sender_line else 'Unknown Sender'

    # Append the benign email content for inspection or further use
    data['benign_content'] = benign_email
    return data

def compose_phishing_email(data: dict) -> EmailMessage:
    """Build EmailMessage with HTML and text fallback, and save HTML to a file."""
    if 'html_body' in data:
        # Use the provided HTML body directly (e.g., from a URL)
        html_body = data['html_body']
    else:
        # Generate the HTML body using the template
        html_body = fill_template(TEMPLATE_HTML, data)

    verify_link = (
        f"https://secure-{data['company_name'].lower()}.com/verify?user={data['username'].replace(' ', '%20')}"
    )
    sender = data.get('sender', f"{data['company_name']} Security Team")
    msg = EmailMessage()
    msg['From']    = f"{sender} <no-reply@{data['company_name'].lower()}.com>"
    msg['To']      = f"{data['honorific']} {data['username']} <{data['username'].replace(' ', '.').lower()}@{data['company_name'].lower()}.com>"
    msg['Subject'] = data['subject']
    fallback = (
        f"Hi {data['honorific']} {data['username']},\n\n"
        f"Please complete a quick security check: {verify_link}\n\n"
        f"This request was initiated by your manager, {data['boss_name']}, to ensure compliance with our latest security policies.\n\n"
        "Thank you,\n"
        f"The {data['company_name']} Security Team"
    )
    msg.set_content(fallback)
    msg.add_alternative(html_body, subtype='html')

    # Save the HTML email to a file
    filename = f"phishing_email_{data['username'].replace(' ', '_').lower()}.html"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(html_body)

    return msg

def main():
    data = get_user_input()

    # Ensure 'company_name' is set based on 'mail_service'
    data['company_name'] = data.get('mail_service', 'Unknown Company')

    # Prompt user for boss's name
    data['boss_name'] = input("Enter the name of the recipient's boss: ").strip()

    # Get benign email input
    benign_source = input("Enter benign email source (file path, URL, or string): ").strip()
    source_type = input("Enter source type (file, url, string): ").strip().lower()
    benign_email = read_benign_email(benign_source, source_type)

    # Merge benign email with user data
    data = merge_benign_email(benign_email, data, source_type)

    email = compose_phishing_email(data)
    # Print full MIME message for inspection
    print(email.as_string())

if __name__ == '__main__':
    main()
