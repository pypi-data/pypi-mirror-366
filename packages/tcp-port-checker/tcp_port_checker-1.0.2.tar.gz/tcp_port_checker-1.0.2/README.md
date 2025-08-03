# 🌐 TCP Port and Ping Checker

A powerful, real-time network connectivity analyzer that performs both ping and TCP port checks with intelligent system resource management.

![Python](https://img.shields.io/badge/python-3.6+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Platform](https://img.shields.io/badge/platform-Linux%20%7C%20Windows%20%7C%20macOS-lightgrey.svg)

## 🚀 Features

- **🔍 Dual Connectivity Check**: Both ping and TCP port verification
- **🌐 IPv6 Support**: Full support for IPv4, IPv6, and domain names
- **⚡ Real-time System Monitoring**: CPU and RAM usage tracking
- **🤖 Dynamic Resource Management**: Auto-adjusting thread count and batch sizes
- **🛡️ Intelligent Throttling**: Automatic slowdown on high system load
- **📊 Comprehensive Reporting**: Beautiful HTML and detailed TXT reports
- **🔧 CLI Support**: Flexible command-line interface
- **🎯 Multi-format Input**: Single IPs, comma-separated lists, or file-based
- **🧵 Thread-safe Operations**: Secure concurrent processing
- **📈 Performance Analytics**: Real-time progress monitoring

## 📁 Project Structure

```
tcp-port-checker/
├── main.py                 # Main application with CLI support
├── config.py               # Configuration and IP loading
├── network_checker.py      # Core network checking logic
├── system_monitor.py       # Real-time system monitoring
├── report_generator.py     # Report generation (TXT/HTML)
├── ip_addresses.txt        # IP addresses list (auto-generated)
├── requirements.txt        # Dependencies
└── README.md              # This file
```

## 🛠️ Installation

### Prerequisites
- **Python 3.6+** (recommended: Python 3.8+)

### Quick Setup
```bash
# Clone the repository
git clone https://github.com/ismailTrk/tcp-port-checker.git
cd tcp-port-checker

# Install dependencies
pip install -r requirements.txt

# Run with default settings
python3 main.py
```

### Dependencies
- `psutil>=5.8.0` - System resource monitoring

All other components use Python standard library.

## 🚀 Usage

### Basic Usage

```bash
# Check IPs from default file (ip_addresses.txt)
python3 main.py

# Quick single IP check
python3 main.py -ip 192.168.1.1

# Check specific port
python3 main.py -ip 192.168.1.1 -p 22

# Check IPv6 addresses
python3 main.py -ip "2001:4860:4860::8888,::1" -p 53

# Mixed IPv4, IPv6, and domains
python3 main.py -ip "8.8.8.8,2001:4860:4860::8888,google.com" -p 443
```

### Advanced Usage

```bash
# Use custom IP file
python3 main.py -f /path/to/custom_ips.txt

# Custom timeout and workers
python3 main.py -ip 10.0.0.1 -t 5 --no-monitor -w 20

# Generate only specific report type
python3 main.py --txt-only -o scan_results

# Complex scan with custom settings
python3 main.py -f /var/network_ips.txt -p 9000 -t 10 -o network_audit
```

### CLI Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| `-ip, --ip-address` | Single IP or comma-separated list | `-ip 192.168.1.1` |
| `-p, --port` | Target port to check | `-p 9000` |
| `-f, --file` | Custom IP list file | `-f /var/ips.txt` |
| `-t, --timeout` | Connection timeout (seconds) | `-t 5` |
| `-o, --output` | Output file prefix | `-o scan_results` |
| `--txt-only` | Generate only TXT report | `--txt-only` |
| `--html-only` | Generate only HTML report | `--html-only` |
| `--no-monitor` | Disable system monitoring | `--no-monitor` |
| `-w, --workers` | Worker thread count (static mode) | `-w 15` |

## 📄 IP Address File Format

Create `ip_addresses.txt` or use custom files:

```txt
# TCP Port Checker - IP Addresses List
# Lines starting with # are comments

# Single IPs
192.168.1.1
10.0.0.1

# Comma-separated IPs
192.168.1.10, 192.168.1.11, 192.168.1.12

# Domain names
google.com
github.com
```

## 📊 System Features

### 🤖 Dynamic Worker Management
- **Low Load** (<30%): CPU_COUNT × 3 workers
- **Medium Load** (30-60%): CPU_COUNT × 2 workers  
- **High Load** (60-80%): CPU_COUNT × 1 worker
- **Critical Load** (>80%): CPU_COUNT ÷ 2 workers

### 📦 Dynamic Batch Processing
- **High Load**: Small batches (×0.4)
- **Normal Load**: Regular batches (×1.0)
- **Low Load**: Large batches (×1.4)

### 🛡️ Intelligent Throttling
- **>95% Usage**: 2-second delays
- **>90% Usage**: 1-second delays
- **>85% Usage**: 0.5-second delays

## 📈 Output Examples

### Console Output
```
🚀 Checking 5 hosts on port 52311
💻 CPU:████████░(87.3%) | RAM:██████░░(75.2%) | Workers:8 | Throttle:🟢

IP ADDRESS      | PING     | PORT       | STATUS
----------------------------------------------------------------------
192.168.1.1     | PING ✓   | TCP52311 ✗ | 🟡 PING OK, PORT CLOSED
10.0.0.1        | PING ✓   | TCP52311 ✓ | 🟢 FULL ACCESS
google.com      | PING ✓   | TCP52311 ✗ | 🟡 PING OK, PORT CLOSED
```

### Status Codes
- 🟢 **FULL ACCESS**: Ping ✓ + Port ✓
- 🟡 **PING OK, PORT CLOSED**: Ping ✓ + Port ✗
- 🟠 **PING FAILED, PORT OPEN**: Ping ✗ + Port ✓
- 🔴 **NO ACCESS**: Ping ✗ + Port ✗

## 🎨 Report Generation

### TXT Report
- Detailed statistics and analysis
- Categorized results by status
- Performance recommendations
- Problem analysis and suggestions

### HTML Report
- Interactive web interface
- Color-coded status indicators
- Real-time filtering
- Responsive design for all devices

## ⚙️ Configuration

Edit `config.py` to customize:

```python
DEFAULT_PORT = 52311                 # Default port to check
DEFAULT_TIMEOUT = 3                  # Connection timeout
MIN_WORKERS = 2                      # Minimum threads
MAX_WORKERS_LIMIT = 50               # Maximum threads
THROTTLE_CPU_THRESHOLD = 85          # CPU throttle threshold
THROTTLE_MEMORY_THRESHOLD = 85       # RAM throttle threshold
```

## 🔧 Development

### Code Structure
- **Modular Design**: Clean separation of concerns
- **PEP 8 Compliant**: Professional Python standards
- **Thread-safe**: RLock protection for shared resources
- **Error Handling**: Comprehensive exception management
- **Type Hints**: Enhanced code readability

### Testing
```bash
# Test with minimal IPs
echo "127.0.0.1" > test_ips.txt
python3 main.py -f test_ips.txt

# Test CLI arguments
python3 main.py -ip 127.0.0.1 -p 22 --txt-only
```

## 🐛 Troubleshooting

### Common Issues

**IP file not found:**
```
❌ IP list file not found: ip_addresses.txt
```
**Solution**: The program will auto-create a sample file. Edit it and run again.

**Permission denied for ping:**
```
❌ Ping command failed
```
**Solution**: On some systems, you may need sudo privileges for ping commands.

**Invalid IP format:**
```
⚠️ Line 5: Invalid IP format skipped: 10.25.1.300
```
**Solution**: Fix IP addresses (values must be 0-255).

### Performance Tips
- Use `--no-monitor` for consistent performance on stable systems
- Adjust `-w` (workers) based on your system capabilities
- Use `-t` (timeout) appropriate for your network latency

## 📋 System Requirements

- **OS**: Linux, Windows, macOS
- **Python**: 3.6+ (recommended: 3.8+)
- **RAM**: Minimum 256MB available
- **CPU**: Any modern processor
- **Network**: Ping command access, TCP socket permissions

## 🤝 Contributing

Contributions are welcome! Please feel free to submit pull requests.

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📝 License

This project is open source and available under the [MIT License](LICENSE).

## 🆘 Support

If you encounter any issues or have questions:
- Open an issue on GitHub
- Check the troubleshooting section
- Review the example usage patterns

---

**⚡ Pro Tip**: Start with `python3 main.py -ip 127.0.0.1` to test the application quickly!