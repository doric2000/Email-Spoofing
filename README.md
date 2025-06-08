# Advanced Phishing Email System with DNS Exfiltration

## Overview
This project demonstrates a complete phishing attack chain for educational and research purposes. The system includes email creation, payload delivery, data collection, and DNS exfiltration capabilities.

### Main Components:
1. **Phishing Email Creation** (`Phishing.py`): Creates sophisticated phishing emails with malicious attachments
2. **Data Collection Payload** (`SecurityCheck`): Python executable that collects system information and exfiltrates it via DNS
3. **DNS Exfiltration Decoder** (`dns_decoder.py`): Decodes and reconstructs data transmitted through DNS queries

## Attack Chain
1. **Email Generation**: Create phishing emails with malicious `SecurityCheck` attachment
2. **Payload Delivery**: Victim downloads and executes the seemingly innocent security tool
3. **Data Collection**: Tool gathers system information (username, hostname, OS details)
4. **DNS Exfiltration**: Data is Base64 encoded, chunked, and transmitted via DNS queries to attacker-controlled domain
5. **Data Reconstruction**: DNS logs are processed to reconstruct the original exfiltrated data

## Features
- **Two Email Creation Methods**:
  - Create phishing email from scratch with custom templates
  - Mimic existing benign emails and inject malicious links
- **Stealth Data Collection**: Disguised as legitimate security check tool
- **DNS Exfiltration**: Covert channel using DNS queries to bypass network security
- **Automatic Payload Attachment**: SecurityCheck file automatically attached to phishing emails
- **Data Reconstruction**: Automatic decoding and JSON export of exfiltrated data
- **Multi-chunk Support**: Handles large data by splitting into DNS-compatible chunks

## Quick Setup

### Automated Installation
For easy setup, use the provided installation script:

```bash
# Make the setup script executable and run it
chmod +x setup.sh
./setup.sh
```

The setup script will automatically:
- Install Python dependencies
- Install and configure BIND9 DNS server
- Create the attacker.local domain
- Configure DNS logging
- Set up DNS client resolution
- Optionally install MailHog for email testing

### Manual Installation
Follow the detailed steps below if you prefer manual installation or need to customize the setup.

## Prerequisites

### System Requirements
- **Operating System**: Linux (tested on Ubuntu/Debian)
- **Python**: Python 3.x with required libraries
- **DNS Server**: BIND9 configured for logging DNS queries
- **Network**: Local network setup for DNS exfiltration testing

### Required Software Installation

#### 1. Python Dependencies
```bash
pip3 install requests beautifulsoup4
```

#### 2. BIND9 DNS Server Setup
```bash
# Install BIND9
sudo apt update
sudo apt install bind9 bind9utils bind9-doc

# Configure DNS logging (add to /etc/bind/named.conf.local)
sudo nano /etc/bind/named.conf.local
```

Add the following zone configuration:
```bash
zone "attacker.local" {
    type master;
    file "/etc/bind/db.attacker.local";
    allow-query { any; };
};

logging {
    channel query_log {
        file "/var/log/named/query.log" versions 3 size 5m;
        severity info;
        print-category yes;
        print-severity yes;
        print-time yes;
    };
    category queries { query_log; };
};
```

#### 3. Create DNS Zone File
```bash
# Create zone file
sudo nano /etc/bind/db.attacker.local
```

Add the following content:
```
$TTL    604800
@       IN      SOA     attacker.local. root.attacker.local. (
                              2         ; Serial
                         604800         ; Refresh
                          86400         ; Retry
                        2419200         ; Expire
                         604800 )       ; Negative Cache TTL
;
@       IN      NS      attacker.local.
@       IN      A       127.0.0.1
*       IN      A       127.0.0.1
```

#### 4. Configure DNS Client
```bash
# Edit DNS resolver configuration
sudo nano /etc/systemd/resolved.conf
```

Add or modify:
```
[Resolve]
DNS=127.0.0.1
Domains=attacker.local
```

#### 5. Restart Services
```bash
# Create log directory
sudo mkdir -p /var/log/named
sudo chown bind:bind /var/log/named

# Restart services
sudo systemctl restart bind9
sudo systemctl restart systemd-resolved

# Verify DNS setup
nslookup test.attacker.local
```

### Optional: MailHog for Email Testing
```bash
# Install MailHog for local email testing
wget https://github.com/mailhog/MailHog/releases/download/v1.0.0/MailHog_linux_amd64
chmod +x MailHog_linux_amd64
sudo mv MailHog_linux_amd64 /usr/local/bin/mailhog
```

## Usage

### Step 1: Start Required Services
```bash
# Start BIND9 DNS server
sudo systemctl start bind9

# Optional: Start MailHog for email testing
MailHog &
```

### Step 2: Generate Phishing Email
```bash
# Run the main phishing script
python3 Phishing.py
```

The script will present two options:
1. **Create phishing email from scratch**: Input recipient details and generate custom phishing email
2. **Mimic existing email and inject malicious link**: Process benign email and inject malicious content

Both options automatically attach the `SecurityCheck` payload to the generated email.

### Step 3: Simulate Victim Actions
1. **Email Reception**: View the generated HTML email file
2. **Download Payload**: Extract the `SecurityCheck` attachment
3. **Execute Payload**: Run the SecurityCheck file (simulates victim execution)
   ```bash
   python3 SecurityCheck
   ```

### Step 4: Monitor DNS Exfiltration
```bash
# Monitor DNS queries in real-time
sudo tail -f /var/log/named/query.log

# Or decode collected data
python3 dns_decoder.py
```

### Step 5: Analyze Results
The decoder will create JSON files with reconstructed data:
```bash
# View latest exfiltrated data
ls -la exfiltrated_data_*.json
cat exfiltrated_data_*.json | jq .
```

## File Structure

```
├── Phishing.py                    # Main phishing email generator
├── SecurityCheck                  # Malicious payload (Python executable)
├── dns_decoder.py                 # DNS exfiltration data decoder
├── setup.sh                       # Automated installation script
├── README.md                      # This documentation
├── *.html                         # Generated phishing emails
├── exfiltrated_data_*.json        # Decoded exfiltration results
└── SecurityCheck.sh               # Backup shell script version
```

## Security Research & Testing

### DNS Exfiltration Analysis
The system demonstrates several advanced techniques:

1. **Data Encoding**: System information is Base64 encoded for transmission
2. **Chunking**: Large data is split into DNS-compatible segments
3. **Subdomain Encoding**: Data embedded in DNS subdomain queries
4. **Steganographic Timing**: Multiple queries with slight delays to avoid detection
5. **Reconstruction**: Automatic reassembly of chunked data

### Example Exfiltrated Data
```json
{
    "session_id": "original_08-Jun-2025",
    "source": "original",
    "timestamp": "08-Jun-2025 18:55:02.308",
    "chunk_count": 2,
    "completed": false,
    "decoded_data": "user:dor|host:unknown|os:Linux-6.8.0-60-gener6_64-with-glibc2.35"
}
```

### Defensive Measures Tested
- DNS query monitoring and analysis
- Suspicious subdomain pattern detection
- Base64 encoding identification
- Payload behavior analysis

## Troubleshooting

### Common Issues

#### DNS Resolution Problems
```bash
# Check DNS configuration
systemctl status bind9
systemctl status systemd-resolved

# Test DNS resolution
nslookup test.attacker.local
dig @127.0.0.1 test.attacker.local
```

#### Permission Issues
```bash
# Fix log file permissions
sudo mkdir -p /var/log/named
sudo chown bind:bind /var/log/named
sudo chmod 755 /var/log/named
```

#### Python Dependencies
```bash
# Install missing packages
pip3 install --user requests beautifulsoup4
```

### Debugging DNS Exfiltration
```bash
# Check if queries are being logged
sudo tail -f /var/log/named/query.log | grep attacker.local

# Verify BIND9 configuration
sudo named-checkconf
sudo named-checkzone attacker.local /etc/bind/db.attacker.local
```

## Authors
- **Dor Cohen** - 211896279
- **Baruh Ifraimov** - 208526012

## Educational Purpose & Legal Disclaimer

### Important Notice
This project is developed **exclusively for educational and cybersecurity research purposes**. It demonstrates advanced phishing techniques and DNS exfiltration methods to help security professionals understand attack vectors and develop appropriate defenses.

### Legal Requirements
- **Authorization Required**: Only use in authorized penetration testing environments
- **Written Permission**: Obtain explicit written consent before testing on any systems
- **Legal Compliance**: Ensure compliance with local cybersecurity and computer crime laws
- **Responsible Disclosure**: Report discovered vulnerabilities through proper channels

### Prohibited Uses
- **Unauthorized Access**: Do not use against systems without explicit permission
- **Malicious Activities**: Prohibited for any illegal or harmful purposes
- **Data Theft**: Do not use to steal or compromise real user data
- **System Damage**: Do not use to damage or disrupt systems or services

### Liability Disclaimer
The authors and contributors of this project:
- Are **NOT responsible** for any misuse of this software
- Provide this code **"AS IS"** without warranty of any kind
- **Disclaim all liability** for damages arising from unauthorized use
- **Strongly recommend** using only in controlled, authorized environments

### Ethical Guidelines
- Use only for **legitimate security research** and **authorized testing**
- **Respect privacy** and confidentiality of all data encountered
- **Follow responsible disclosure** practices for any vulnerabilities found
- **Contribute to cybersecurity defense** rather than malicious exploitation

**By using this software, you acknowledge that you have read, understood, and agree to comply with these terms and all applicable laws.**
