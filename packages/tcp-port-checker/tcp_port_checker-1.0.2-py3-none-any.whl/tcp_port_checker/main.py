#!/usr/bin/env python3
"""
TCP Port and Ping Checker Application
Main execution file with CLI support
"""

import argparse
import signal
import sys
from pathlib import Path

from .network_checker import NetworkChecker
from .config import (
    DEFAULT_PORT, DEFAULT_TIMEOUT, TXT_OUTPUT_FILE, HTML_OUTPUT_FILE,
    load_ip_addresses, create_sample_ip_file
)


def signal_handler(signum, frame):
    """Handle Ctrl+C signal"""
    print("\n\n⚠️  Operation cancelled by user!")
    sys.exit(0)


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="TCP Port and Ping Checker - Network Connectivity Analyzer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                                    # Check IPs from ip_addresses.txt
  %(prog)s -ip 192.168.1.1                  # Check single IP
  %(prog)s -ip "google.com,github.com"      # Check multiple IPs
  %(prog)s -ip 10.0.0.1 -p 22              # Check specific port
  %(prog)s -f /path/to/ips.txt -p 443       # Use custom IP file
  %(prog)s --txt-only -o scan_results       # Generate only TXT report
        """
    )
    
    parser.add_argument(
        '-ip', '--ip-address',
        type=str,
        help='Single IP address or comma-separated list (e.g., "192.168.1.1,10.0.0.1")'
    )
    
    parser.add_argument(
        '-p', '--port',
        type=int,
        default=DEFAULT_PORT,
        help=f'Port number to check (default: {DEFAULT_PORT})'
    )
    
    parser.add_argument(
        '-f', '--file',
        type=str,
        help='Custom IP list file path'
    )
    
    parser.add_argument(
        '-t', '--timeout',
        type=int,
        default=DEFAULT_TIMEOUT,
        help=f'Connection timeout in seconds (default: {DEFAULT_TIMEOUT})'
    )
    
    parser.add_argument(
        '-o', '--output',
        type=str,
        help='Output file prefix (default: port_check_results)'
    )
    
    parser.add_argument(
        '--txt-only',
        action='store_true',
        help='Generate only TXT report'
    )
    
    parser.add_argument(
        '--html-only',
        action='store_true',
        help='Generate only HTML report'
    )
    
    parser.add_argument(
        '--no-monitor',
        action='store_true',
        help='Disable real-time system monitoring'
    )
    
    parser.add_argument(
        '-w', '--workers',
        type=int,
        help='Number of worker threads (static mode only)'
    )
    
    parser.add_argument(
        '-v', '--version',
        action='version',
        version='TCP Port Checker v1.0.0'
    )
    
    return parser.parse_args()


def get_ip_addresses(args):
    """Get IP addresses from arguments or file"""
    if args.ip_address:
        # Parse comma-separated IPs
        ip_list = [ip.strip() for ip in args.ip_address.split(',')]
        print(f"✅ {len(ip_list)} IP addresses from command line")
        return ip_list
    
    elif args.file:
        # Load from custom file
        return load_ip_addresses(args.file)
    
    else:
        # Load from default file
        return load_ip_addresses()


def main():
    """Main function"""
    # Handle Ctrl+C gracefully
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        # Parse command line arguments
        args = parse_arguments()
        
        print("🌐 TCP Port and Ping Checker")
        print("=" * 50)
        
        # Get IP addresses
        try:
            ip_addresses = get_ip_addresses(args)
        except FileNotFoundError:
            print("📝 IP list file not found, creating sample file...")
            create_sample_ip_file()
            print("\n🔄 Please edit 'ip_addresses.txt' and run again.")
            print("💡 Example: Add IPs like '10.25.1.1' or domains like 'google.com'")
            return
        except ValueError as e:
            print(f"❌ {str(e)}")
            return
        
        # Validate arguments
        if args.txt_only and args.html_only:
            print("❌ Cannot use --txt-only and --html-only together")
            return
        
        print(f"🚀 Checking {len(ip_addresses)} hosts on port {args.port}")
        print("⏳ Please wait, this may take some time...")
        print("💡 Press Ctrl+C to cancel")
        
        # Create NetworkChecker instance
        checker = NetworkChecker(timeout=args.timeout)
        
        # Choose monitoring mode
        if args.no_monitor and args.workers:
            # Static mode with fixed workers
            print(f"🔧 Static mode: {args.workers} workers")
            results = checker.check_multiple_hosts_static(
                ip_addresses, 
                port=args.port,
                max_workers=args.workers
            )
        elif args.no_monitor:
            # Static mode with default workers
            print("🔧 Static mode: auto workers")
            results = checker.check_multiple_hosts_static(
                ip_addresses, 
                port=args.port
            )
        else:
            # Dynamic mode with system monitoring
            print("🤖 Dynamic mode: real-time monitoring")
            results = checker.check_multiple_hosts(
                ip_addresses, 
                port=args.port
            )
        
        # Save results
        print("\n💾 Saving results...")
        
        # Determine output filenames
        if args.output:
            txt_file = f"{args.output}.txt"
            html_file = f"{args.output}.html"
        else:
            txt_file = TXT_OUTPUT_FILE
            html_file = HTML_OUTPUT_FILE
        
        # Generate reports based on arguments
        if not args.html_only:
            checker.save_to_txt(results, txt_file)
        
        if not args.txt_only:
            checker.save_to_html(results, html_file)
        
        # Show completion message
        print("\n✅ Scan completed!")
        if not args.html_only:
            print(f"📄 TXT report: '{txt_file}'")
        if not args.txt_only:
            print(f"🌐 HTML report: '{html_file}'")
        
        # Quick summary
        total = len(results)
        ping_ok = len([r for r in results if "PING ✓" in r])
        port_ok = len([r for r in results if f"TCP{args.port} ✓" in r])
        full_access = len([r for r in results if "FULL ACCESS" in r])
        
        print(f"\n📊 QUICK SUMMARY:")
        print(f"   Total Hosts: {total}")
        print(f"   Ping Success: {ping_ok}/{total} ({ping_ok/total*100:.1f}%)")
        print(f"   Port Open: {port_ok}/{total} ({port_ok/total*100:.1f}%)")
        print(f"   Full Access: {full_access}/{total} ({full_access/total*100:.1f}%)")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Operation cancelled by user!")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error occurred: {str(e)}")
        print("🔍 Check logs for details or try again")
        sys.exit(1)


if __name__ == "__main__":
    main()
