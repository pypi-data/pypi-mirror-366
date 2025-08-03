"""
Configuration settings
TCP Port and Ping Checker Application
"""

import os
import re

# Default settings
DEFAULT_PORT = 52311
DEFAULT_TIMEOUT = 3

# Dynamic worker calculation settings
MIN_WORKERS = 2              # Minimum thread count
MAX_WORKERS_MULTIPLIER = 2   # Multiplier of CPU core count
MAX_WORKERS_LIMIT = 50       # Maximum thread limit (for security)

# System monitor settings
MONITOR_INTERVAL = 0.3       # System check interval (seconds)
THROTTLE_CPU_THRESHOLD = 85  # CPU throttle threshold (%)
THROTTLE_MEMORY_THRESHOLD = 85  # RAM throttle threshold (%)

# File paths
IP_LIST_FILE = "ip_addresses.txt"  # IP list file
TXT_OUTPUT_FILE = "port_check_results.txt"
HTML_OUTPUT_FILE = "port_check_results.html"


def load_ip_addresses(filename=IP_LIST_FILE):
    """
    Load IP addresses from file
    
    Args:
        filename (str): IP list file name
        
    Returns:
        list: List of IP addresses
        
    Raises:
        FileNotFoundError: If file not found
        ValueError: If invalid IP format found
    """
    if not os.path.exists(filename):
        raise FileNotFoundError(
            f"❌ IP list file not found: {filename}\n"
            f"Please create '{filename}' and add IP addresses."
        )
    
    ip_addresses = []
    
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            for line_num, line in enumerate(file, 1):
                line = line.strip()
                
                # Skip empty lines and comments
                if not line or line.startswith('#'):
                    continue
                
                # Process comma-separated IPs
                if ',' in line:
                    ips = [ip.strip() for ip in line.split(',')]
                else:
                    ips = [line]
                
                # Check and add each IP
                for ip in ips:
                    if ip:  # Empty string check
                        if _is_valid_ip_format(ip):
                            ip_addresses.append(ip)
                        else:
                            print(f"⚠️  Line {line_num}: Invalid IP format skipped: {ip}")
    
    except Exception as e:
        raise ValueError(f"❌ Error reading IP list: {str(e)}")
    
    if not ip_addresses:
        raise ValueError(f"❌ No valid IP addresses found in '{filename}'!")
    
    print(f"✅ {len(ip_addresses)} IP addresses loaded from '{filename}'")
    return ip_addresses


def _is_valid_ip_format(ip_str):
    """
    Simple IP format validation for IPv4, IPv6, and domain names
    
    Args:
        ip_str (str): IP string to check
        
    Returns:
        bool: True if valid format
    """
    # For domain names (e.g., google.com)
    if '.' in ip_str and not ip_str.replace('.', '').replace('-', '').isdigit():
        # Basic domain validation
        domain_pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*$'
        return bool(re.match(domain_pattern, ip_str))
    
    # For IPv6 addresses (basic check)
    if ':' in ip_str:
        # Basic IPv6 validation
        parts = ip_str.split(':')
        if 2 <= len(parts) <= 8:
            for part in parts:
                if part == '':  # Allow empty parts for ::
                    continue
                if len(part) > 4:  # Each part max 4 hex digits
                    return False
                try:
                    int(part, 16)  # Must be valid hex
                except ValueError:
                    return False
            return True
        return False
    
    # For IPv4 addresses
    parts = ip_str.split('.')
    if len(parts) == 4:
        try:
            for part in parts:
                num = int(part)
                if not (0 <= num <= 255):
                    return False
            return True
        except ValueError:
            return False
    
    return False


def create_sample_ip_file(filename=IP_LIST_FILE):
    """
    Create sample IP list file
    
    Args:
        filename (str): File name to create
    """
    sample_content = """# TCP Port Checker - IP Addresses List
# Write one IP address per line
# You can use comma-separated IPs on the same line
# Lines starting with # are treated as comments
# Supports IPv4, IPv6, and domain names

# Example usage:
192.168.1.1
10.0.0.1, 10.0.0.2, 10.0.0.3
google.com

# IPv6 examples:
# 2001:db8::1
# ::1
# fe80::1
# 2001:4860:4860::8888, 2001:4860:4860::8844

# Add your IP addresses below:
# 192.168.1.100
# 10.0.1.1, 10.0.1.2
# example.com

# Domain names are also supported:
# google.com
# github.com
# ipv6.google.com
"""
    
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(sample_content)
    
    print(f"✅ Sample IP list file created: {filename}")
    print(f"📝 Edit the file to add your IP addresses")