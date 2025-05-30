import requests
import re

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
    # Check for existing links in the benign email
    link_pattern = re.compile(r'<a\s+href=["\"](.*?)["\"]>', re.IGNORECASE)
    links = link_pattern.findall(benign_email)

    if links:
        # Replace the first link with the malicious link
        malicious_link = f"https://secure-{data['company_name'].lower()}.com/verify?user={data['username'].replace(' ', '%20')}"
        benign_email = link_pattern.sub(f'<a href="{malicious_link}">', benign_email, count=1)
    else:
        # Add a button with the malicious link if no links are found
        malicious_link = f"https://secure-{data['company_name'].lower()}.com/verify?user={data['username'].replace(' ', '%20')}"
        button_html = (
            f'<p>To ensure your account security, please click the button below:</p>'
            f'<p><a href="{malicious_link}" class="button" style="display:inline-block; padding:10px 20px; background-color:#004080; color:white; text-decoration:none; border-radius:5px;">Verify Now</a></p>'
        )
        benign_email = benign_email.replace('</body>', f'{button_html}</body>')

    # Use dynamic data to enhance the email content
    benign_email = benign_email.replace('Dear Employee,', f'Dear {data["honorific"]} {data["username"]},')
    benign_email = benign_email.replace('Company Security Team', f'{data["company_name"]} Security Team')
    benign_email = benign_email.replace('Joseph', data['boss_name'])

    # Append the modified benign email content for inspection or further use
    data['html_body'] = benign_email
    return data
