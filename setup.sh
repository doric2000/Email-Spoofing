#!/bin/bash

# Advanced Phishing Email System - Setup Script
# Educational and Research Purposes Only

echo "=================================================="
echo "Advanced Phishing Email System Setup"
echo "Educational and Research Purposes Only"
echo "=================================================="

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root for some operations
check_root() {
    if [[ $EUID -eq 0 ]]; then
        print_error "This script should not be run as root for safety reasons"
        print_status "Please run as a regular user. Sudo will be used when needed."
        exit 1
    fi
}

# Install Python dependencies
install_python_deps() {
    print_status "Installing Python dependencies..."
    pip3 install --user requests beautifulsoup4
    if [ $? -eq 0 ]; then
        print_status "Python dependencies installed successfully"
    else
        print_error "Failed to install Python dependencies"
        return 1
    fi
}

# Install BIND9
install_bind9() {
    print_status "Installing BIND9 DNS server..."
    sudo apt update
    sudo apt install -y bind9 bind9utils bind9-doc
    if [ $? -eq 0 ]; then
        print_status "BIND9 installed successfully"
    else
        print_error "Failed to install BIND9"
        return 1
    fi
}

# Configure BIND9
configure_bind9() {
    print_status "Configuring BIND9..."
    
    # Backup original configuration
    sudo cp /etc/bind/named.conf.local /etc/bind/named.conf.local.backup
    
    # Add zone configuration
    sudo tee -a /etc/bind/named.conf.local > /dev/null << 'EOF'

// Attacker domain for DNS exfiltration testing
zone "attacker.local" {
    type master;
    file "/etc/bind/db.attacker.local";
    allow-query { any; };
};

// DNS query logging configuration
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
EOF

    # Create zone file
    sudo tee /etc/bind/db.attacker.local > /dev/null << 'EOF'
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
EOF

    # Create log directory
    sudo mkdir -p /var/log/named
    sudo chown bind:bind /var/log/named
    sudo chmod 755 /var/log/named
    
    print_status "BIND9 configuration completed"
}

# Configure DNS client
configure_dns_client() {
    print_status "Configuring DNS client..."
    
    # Backup original resolved configuration
    sudo cp /etc/systemd/resolved.conf /etc/systemd/resolved.conf.backup
    
    # Configure systemd-resolved
    sudo tee /etc/systemd/resolved.conf > /dev/null << 'EOF'
[Resolve]
DNS=127.0.0.1
Domains=attacker.local
EOF
    
    print_status "DNS client configuration completed"
}

# Restart services
restart_services() {
    print_status "Restarting services..."
    
    # Check BIND9 configuration
    sudo named-checkconf
    if [ $? -ne 0 ]; then
        print_error "BIND9 configuration check failed"
        return 1
    fi
    
    sudo named-checkzone attacker.local /etc/bind/db.attacker.local
    if [ $? -ne 0 ]; then
        print_error "Zone file check failed"
        return 1
    fi
    
    # Restart services
    sudo systemctl restart bind9
    sudo systemctl restart systemd-resolved
    
    # Enable services
    sudo systemctl enable bind9
    
    print_status "Services restarted successfully"
}

# Test DNS configuration
test_dns() {
    print_status "Testing DNS configuration..."
    
    sleep 3  # Give services time to start
    
    # Test DNS resolution
    nslookup test.attacker.local > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        print_status "DNS test successful"
    else
        print_warning "DNS test failed - you may need to restart or check configuration"
    fi
    
    # Test if logs are being written
    echo "test query" | nslookup test.attacker.local > /dev/null 2>&1
    if sudo test -f /var/log/named/query.log; then
        print_status "DNS logging is working"
    else
        print_warning "DNS logging may not be working properly"
    fi
}

# Install MailHog (optional)
install_mailhog() {
    read -p "Do you want to install MailHog for email testing? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_status "Installing MailHog..."
        wget -q https://github.com/mailhog/MailHog/releases/download/v1.0.0/MailHog_linux_amd64
        if [ $? -eq 0 ]; then
            chmod +x MailHog_linux_amd64
            sudo mv MailHog_linux_amd64 /usr/local/bin/mailhog
            print_status "MailHog installed successfully"
            print_status "You can start it with: mailhog"
        else
            print_warning "Failed to download MailHog"
        fi
    fi
}

# Main setup function
main() {
    check_root
    
    print_status "Starting setup process..."
    
    # Install components
    install_python_deps || exit 1
    install_bind9 || exit 1
    configure_bind9 || exit 1
    configure_dns_client || exit 1
    restart_services || exit 1
    test_dns
    install_mailhog
    
    print_status "=================================================="
    print_status "Setup completed successfully!"
    print_status "=================================================="
    print_status ""
    print_status "Next steps:"
    print_status "1. Run: python3 Phishing.py"
    print_status "2. Generate a phishing email"
    print_status "3. Execute the SecurityCheck payload"
    print_status "4. Run: python3 dns_decoder.py"
    print_status ""
    print_status "Optional: Start MailHog with: mailhog"
    print_status "View MailHog interface at: http://localhost:8025"
    print_status ""
    print_warning "Remember: This is for educational purposes only!"
}

# Run main function
main "$@"
