# Email Spoofing Project

## Overview
This project demonstrates how to create and test phishing emails for educational and research purposes. The script `EmailSpoofing.py` provides two main functionalities:

1. **Create a phishing email from scratch**: Users can input recipient details, company name, and other information to generate a phishing email using a predefined HTML template.
2. **Mimic an existing email**: The script can read a benign email (from a file, URL, or string), inject a malicious link, and save the modified email for testing purposes.

## Features
- **Dynamic Email Composition**: Placeholders in the HTML template are dynamically replaced with user-provided data.
- **MailHog Integration**: Allows testing emails locally without sending them to real recipients.
- **Error Handling**: Includes robust error handling for invalid inputs and SMTP configurations.
- **Malicious Link Injection**: Replaces or adds links in benign emails with malicious ones for testing.

## Usage

### Prerequisites
- Python 3.x
- MailHog (for local email testing)

### Running the Script
1. Clone the repository or download the script.
2. Run the script using the following command:
   ```bash
   python3 EmailSpoofing.py
   ```
3. Follow the prompts to:
   - Create a phishing email from scratch.
   - Mimic an existing email and inject a malicious link.

### Testing with MailHog
- Start MailHog on your local machine:
  ```bash
  mailhog
  ```
- Use the MailHog option in the script to send emails to `localhost:1025`.
- Open the MailHog web interface (usually at `http://localhost:8025`) to view captured emails.

## Authors
- Dor Cohen - 211896279
- Baruh Ifraimov - 208526012

## Disclaimer
This project is for educational purposes only. Do not use it for malicious activities. The authors are not responsible for any misuse of this script.
