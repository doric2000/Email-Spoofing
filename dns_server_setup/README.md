# DNS Exfiltration Server (BIND9) - Quick Guide

This guide explains setting up a BIND9 DNS server to receive data via DNS queries.

**Server IP (for client):** `10.211.55.7`
**Local Domain:** `mylocal.net`

## 1. Setup (New User - Ubuntu/Debian)

### 1.1. Install BIND9
```bash
sudo apt update
sudo apt install bind9 bind9utils -y
```

### 1.2. Free Up Port 53 (If systemd-resolved is using it)
```bash
sudo systemctl stop systemd-resolved
sudo systemctl disable systemd-resolved
sudo rm /etc/resolv.conf
echo "nameserver 8.8.8.8" | sudo tee /etc/resolv.conf
echo "nameserver 1.1.1.1" | sudo tee -a /etc/resolv.conf
```

### 1.3. Prepare Configuration Files
The necessary configuration files (`named.conf.options`, `named.conf.local`, `db.mylocal.net`, `db.10.211.55`) should be in your project directory (e.g., `/home/parallels/Documents/dns_server/`).

**a. Create BIND directories:**
```bash
sudo mkdir -p /etc/bind/zones
sudo mkdir -p /var/log/named
```

**b. Copy configuration files to BIND's system directories:**
```bash
# Assuming your project files are in ./
sudo cp ./named.conf.options /etc/bind/named.conf.options
sudo cp ./named.conf.local /etc/bind/named.conf.local
sudo cp ./db.mylocal.net /etc/bind/zones/db.mylocal.net
sudo cp ./db.10.211.55 /etc/bind/zones/db.10.211.55
```

**c. Set permissions:**
```bash
sudo chown bind:bind /etc/bind/zones/*
sudo chmod 644 /etc/bind/zones/*
sudo chown bind:bind /var/log/named
sudo chmod 755 /var/log/named
```

## 2. Key Configuration: Query Logging
Query logging is enabled in `/etc/bind/named.conf.options`. This logs incoming DNS queries (containing the data) to `/var/log/named/query.log`.
```
// Snippet from named.conf.options
logging {
  channel query_log {
    file "/var/log/named/query.log" versions 5 size 10m;
    severity info;
    print-time yes;
    // ... other print options ...
  };
  category queries { query_log; };
  category default { query_log; };
};
```

## 3. Running the Server

### 3.1. Check Configuration
```bash
sudo named-checkconf
sudo named-checkzone mylocal.net /etc/bind/zones/db.mylocal.net
sudo named-checkzone 55.211.10.in-addr.arpa /etc/bind/zones/db.10.211.55
```
(No output from `named-checkconf` and "OK" from `named-checkzone` means success.)

### 3.2. Start/Restart BIND9
```bash
sudo systemctl restart bind9
```

### 3.3. Check Status
```bash
sudo systemctl status bind9
```
(Look for "active (running)".)

### 3.4. Enable on Boot (Optional)
```bash
sudo systemctl enable bind9
```

## 4. Checking Received Data ("Messages")

Data is sent encoded in DNS queries. These queries are logged.

### 4.1. Log File Location
`/var/log/named/query.log`

### 4.2. View Logs
*   Live view: `sudo tail -f /var/log/named/query.log`
*   Full view: `sudo less /var/log/named/query.log`

### 4.3. How Data Appears
Client sends data like `encoded_chunk.your_label.mylocal.net`.
Log entry will show: `... client X.X.X.X#port (encoded_chunk.your_label.mylocal.net): query: encoded_chunk.your_label.mylocal.net IN A ...`

### 4.4. Processing Logs to a "received" File
You need a script to:
1.  Read `/var/log/named/query.log`.
2.  Filter queries for your specific label (e.g., `*.your_label.mylocal.net`).
3.  Extract `encoded_chunk`.
4.  Decode and reassemble the chunks.
5.  Save to a file (e.g., `received_data.txt`).

### 4.5. Using the `dns_log_decoder.py` Script
A Python script `dns_log_decoder.py` is provided in this project to automate step 4.4.

**a. Configuration (Important!):**
   - **Open `dns_log_decoder.py`**.
   - **Modify `DEFAULT_TARGET_DOMAIN_SUFFIX`**: Change `"exfil.mylocal.net"` to the actual suffix your client executable will use. For example, if your client sends queries like `dataChunk.secretops.mylocal.net`, set this to `"secretops.mylocal.net"`.
   - You can also change `DEFAULT_ENCODING` (default is "hex") if your client uses a different encoding (e.g., "base64").

**b. Running the script:**
   - To use default settings (after configuring the suffix in the script):
     ```bash
     # May need sudo to read /var/log/named/query.log
     sudo python3 /home/parallels/Documents/dns_server/dns_log_decoder.py
     ```
   - The decoded data will be saved to `received_data.txt` by default.

   - To specify options via command line:
     ```bash
     python3 /home/parallels/Documents/dns_server/dns_log_decoder.py \\
             --log-file /path/to/your/query.log \\
             --target-suffix yourlabel.mylocal.net \\
             --output-file custom_output.txt \\
             --encoding base64
     ```
   - If you don\'t use `sudo` for the default log file, ensure the script has read access to it (e.g., copy the log file to your current directory and use `--log-file ./query.log`).

## 5. Client Executable (Brief)
The client (on Linux/Windows) should:
1.  Encode data into DNS-safe chunks (e.g., hex, base64).
2.  Craft DNS queries: `[chunk].[sequence_id].your_label.mylocal.net`.
3.  Send queries to this server\'s IP: `10.211.55.7`.

## 6. File Overview

-   `named.conf.options`: Main BIND9 configuration file for global options, including the critical query logging setup.
-   `named.conf.local`: BIND9 configuration file used to define local zones (e.g., `mylocal.net` and the reverse lookup zone).
-   `db.mylocal.net`: BIND9 zone file that defines DNS records for the `mylocal.net` domain. This is where `ns1.mylocal.net` is typically defined.
-   `db.10.211.55`: BIND9 reverse zone file that defines pointer (PTR) records for the `10.211.55.x` IP address range, allowing reverse DNS lookups.
-   `dns_log_decoder.py`: Python script to parse BIND9 query logs. It extracts data chunks from hostnames matching a specific suffix (e.g., `data0.ENCODED_CHUNK.ns1.mylocal.net`), decodes them (defaulting to Base64), reassembles them in order, and saves the complete message. (Detailed in section 4.5).
-   `README.md`: This setup guide and documentation file.
-   `received_data_*.txt`: Timestamped text files (e.g., `received_data_YYYYMMDD_HHMMSS.txt`) where the fully decoded and reassembled exfiltrated data is saved by `dns_log_decoder.py`.
