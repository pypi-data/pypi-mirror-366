"""
Network connectivity checker class
Integrated with real-time system monitoring
"""

import socket
import subprocess
import platform
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Event

from .config import TXT_OUTPUT_FILE, HTML_OUTPUT_FILE
from .report_generator import ReportGenerator
from .system_monitor import SystemMonitor


class NetworkChecker:
    """Main class for network connectivity checking"""
    
    def __init__(self, timeout=5):
        """
        Initialize NetworkChecker
        
        Args:
            timeout (int): Connection timeout duration
        """
        self.timeout = timeout
        self.report_generator = ReportGenerator()
        self.total_scanned = 0
        self.stop_event = Event()  # For emergency stop
    
    def ping_host(self, ip_address):
        """
        Check host reachability by pinging
        
        Args:
            ip_address (str): IP address to check
            
        Returns:
            bool: True if ping successful, False otherwise
        """
        try:
            # Ping command based on operating system
            param = "-n" if platform.system().lower() == "windows" else "-c"
            timeout_param = "-W" if platform.system().lower() == "windows" else "-w"
            
            command = [
                "ping", param, "1", 
                timeout_param, str(self.timeout), 
                ip_address
            ]
            
            result = subprocess.run(
                command, 
                capture_output=True, 
                text=True, 
                timeout=self.timeout + 2
            )
            return result.returncode == 0
            
        except Exception:
            return False
    
    def check_port(self, ip_address, port):
        """
        Check if TCP port is open on specified IP address (supports IPv4 and IPv6)
        
        Args:
            ip_address (str): IP address to check
            port (int): Port number to check
            
        Returns:
            bool: True if port is open, False otherwise
        """
        try:
            # Determine if it's IPv6
            if ':' in ip_address and not ip_address.startswith('['):
                # IPv6 - wrap in brackets for socket connection
                target_ip = ip_address
                family = socket.AF_INET6
            else:
                # IPv4 or domain name
                target_ip = ip_address
                family = socket.AF_INET
            
            # Try to create appropriate socket
            sock = socket.socket(family, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            
            if family == socket.AF_INET6:
                # For IPv6, we need to handle the address format
                result = sock.connect_ex((target_ip, port))
            else:
                result = sock.connect_ex((target_ip, port))
            
            sock.close()
            return result == 0
            
        except socket.gaierror:
            # DNS resolution failed or invalid address
            return False
        except Exception:
            return False
    
    def check_host_and_port(self, ip_address, port):
        """
        Perform both ping and port checking
        
        Args:
            ip_address (str): IP address to check
            port (int): Port number to check
            
        Returns:
            str: Formatted check result
        """
        ip_clean = ip_address.strip()
        
        # Ping check
        ping_result = self.ping_host(ip_clean)
        ping_status = "PING ✓" if ping_result else "PING ✗"
        
        # Port check
        port_result = self.check_port(ip_clean, port)
        port_status = f"TCP{port} ✓" if port_result else f"TCP{port} ✗"
        
        # Determine overall status
        status = self._determine_status(ping_result, port_result)
        
        return f"{ip_clean:15} | {ping_status:8} | {port_status:10} | {status}"
    
    def _determine_status(self, ping_result, port_result):
        """
        Determine overall status based on ping and port results
        
        Args:
            ping_result (bool): Ping result
            port_result (bool): Port check result
            
        Returns:
            str: Overall status message
        """
        if ping_result and port_result:
            return "🟢 FULL ACCESS"
        elif ping_result and not port_result:
            return "🟡 PING OK, PORT CLOSED"
        elif not ping_result and port_result:
            return "🟠 PING FAILED, PORT OPEN"
        else:
            return "🔴 NO ACCESS"
    
    def check_multiple_hosts(self, ip_list, port):
        """
        Check multiple IP addresses with real-time system monitoring
        
        Args:
            ip_list (list): List of IP addresses
            port (int): Port number to check
            
        Returns:
            list: List of check results
        """
        total_hosts = len(ip_list)
        all_results = []
        
        print(f"🚀 Checking {total_hosts} hosts...")
        print("=" * 70)
        print(f"{'IP ADDRESS':15} | {'PING':8} | {'PORT':10} | STATUS")
        print("-" * 70)
        
        # Start system monitor
        with SystemMonitor(check_interval=0.3) as monitor:
            time.sleep(1.0)  # Wait for monitor to start
            
            remaining_hosts = ip_list.copy()
            batch_count = 0
            
            while remaining_hosts and not self.stop_event.is_set():
                batch_count += 1
                
                # Get current system status
                stats = monitor.get_current_stats()
                current_workers = stats['recommended_workers']
                
                # Calculate dynamic batch size
                batch_size = monitor.calculate_dynamic_batch_size(
                    len(remaining_hosts), 
                    current_workers
                )
                
                # Get current batch
                current_batch = remaining_hosts[:batch_size]
                remaining_hosts = remaining_hosts[batch_size:]
                
                print(f"\n📦 Batch {batch_count} - {len(current_batch)} hosts, "
                      f"{current_workers} workers")
                
                # Throttle control
                throttle_delay = monitor.get_throttle_delay()
                if throttle_delay > 0:
                    print(f"⏳ Throttling active - waiting {throttle_delay}s...")
                    time.sleep(throttle_delay)
                
                # Process batch
                batch_results = self._process_batch_with_monitoring(
                    current_batch, port, current_workers, monitor
                )
                
                # Combine results
                all_results.extend(batch_results)
                
                # Display results
                for result in batch_results:
                    print(result)
                
                # Dynamic delay between batches
                if remaining_hosts:
                    inter_batch_delay = self._calculate_inter_batch_delay(monitor)
                    if inter_batch_delay > 0:
                        time.sleep(inter_batch_delay)
        
        print(f"\n✅ Total {len(all_results)} hosts checked")
        return all_results
    
    def check_multiple_hosts_static(self, ip_list, port, max_workers=10):
        """
        Static mode: Check multiple IPs without system monitoring
        
        Args:
            ip_list (list): List of IP addresses
            port (int): Port number to check
            max_workers (int): Fixed number of worker threads
            
        Returns:
            list: Check results
        """
        total_hosts = len(ip_list)
        
        print(f"🚀 Checking {total_hosts} hosts (Static mode)...")
        print("=" * 70)
        print(f"{'IP ADDRESS':15} | {'PING':8} | {'PORT':10} | STATUS")
        print("-" * 70)
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            results = list(
                executor.map(
                    lambda ip: self._safe_check_host(ip, port), 
                    ip_list
                )
            )
        
        for result in results:
            print(result)
        
        print(f"\n✅ Total {len(results)} hosts checked")
        return results
    
    def _process_batch_with_monitoring(self, batch, port, max_workers, monitor):
        """
        Process a batch with system monitoring
        
        Args:
            batch (list): List of IPs to process
            port (int): Port number
            max_workers (int): Maximum worker count
            monitor (SystemMonitor): System monitor instance
            
        Returns:
            list: Batch results
        """
        results = []
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            future_to_ip = {
                executor.submit(self._safe_check_host, ip, port): ip 
                for ip in batch
            }
            
            # Get results in real-time
            for future in as_completed(future_to_ip):
                if self.stop_event.is_set():
                    break
                
                try:
                    result = future.result(timeout=self.timeout + 2)
                    results.append(result)
                    
                    # Show real-time stats
                    monitor.print_realtime_stats()
                    
                except Exception as e:
                    ip = future_to_ip[future]
                    error_result = f"{ip:15} | PING ✗   | TCP{port} ✗ | 🔴 TIMEOUT"
                    results.append(error_result)
        
        print()  # Line break
        return results
    
    def _calculate_inter_batch_delay(self, monitor):
        """
        Calculate dynamic delay between batches
        
        Args:
            monitor (SystemMonitor): System monitor instance
            
        Returns:
            float: Delay duration
        """
        stats = monitor.get_current_stats()
        cpu_percent = stats['cpu_percent']
        memory_percent = stats['memory_percent']
        
        max_usage = max(cpu_percent, memory_percent)
        
        if max_usage > 85:
            return 1.0  # High load - long break
        elif max_usage > 70:
            return 0.5  # Medium load - medium break
        elif max_usage > 50:
            return 0.2  # Low load - short break
        else:
            return 0.0  # Very low load - no break
    
    def _safe_check_host(self, ip_address, port):
        """
        Safe host checking with error handling
        
        Args:
            ip_address (str): IP address
            port (int): Port number
            
        Returns:
            str: Check result
        """
        try:
            return self.check_host_and_port(ip_address, port)
        except Exception as e:
            # Safe fallback on error
            ip_clean = ip_address.strip()
            return f"{ip_clean:15} | PING ✗   | TCP{port} ✗ | 🔴 ERROR: {str(e)[:20]}"
    
    def emergency_stop(self):
        """Emergency stop for scanning"""
        print("\n🚨 Emergency stop activated!")
        self.stop_event.set()
    
    def save_to_txt(self, results, filename=None):
        """
        Save results to TXT file
        
        Args:
            results (list): Check results
            filename (str, optional): File name
        """
        if filename is None:
            filename = TXT_OUTPUT_FILE
        
        self.report_generator.generate_txt_report(results, filename)
    
    def save_to_html(self, results, filename=None):
        """
        Save results to HTML file
        
        Args:
            results (list): Check results
            filename (str, optional): File name
        """
        if filename is None:
            filename = HTML_OUTPUT_FILE
        
        self.report_generator.generate_html_report(results, filename)
