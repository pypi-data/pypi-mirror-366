"""
Real-time system monitor
Runs in background and continuously monitors system status
"""

import threading
import time
import psutil
from collections import deque
from datetime import datetime
from .config import (
    MIN_WORKERS, MAX_WORKERS_MULTIPLIER, MAX_WORKERS_LIMIT,
    MONITOR_INTERVAL, THROTTLE_CPU_THRESHOLD, THROTTLE_MEMORY_THRESHOLD
)


class SystemMonitor:
    """Real-time system monitor class"""
    
    def __init__(self, check_interval=None):
        """
        Initialize system monitor
        
        Args:
            check_interval (float): Check interval in seconds
        """
        self.check_interval = check_interval or MONITOR_INTERVAL
        self.is_monitoring = False
        self.monitor_thread = None
        self.lock = threading.RLock()  # Thread-safe access
        
        # System status data
        self.current_stats = {
            'cpu_percent': 0.0,
            'memory_percent': 0.0,
            'cpu_count': psutil.cpu_count() or 2,
            'memory_total_gb': psutil.virtual_memory().total / (1024**3),
            'last_update': None,
            'should_throttle': False,
            'recommended_workers': MIN_WORKERS,
            'uptime_seconds': 0
        }
        
        # Historical data (for trend analysis)
        self.cpu_history = deque(maxlen=20)
        self.memory_history = deque(maxlen=20)
        
        # Throttle status
        self.throttle_active = False
        self.throttle_start_time = None
        self.total_throttle_time = 0.0
        
        # Statistics
        self.monitor_start_time = None
        self.total_measurements = 0
    
    def start_monitoring(self):
        """Start system monitoring"""
        if self.is_monitoring:
            return
        
        self.is_monitoring = True
        self.monitor_start_time = time.time()
        
        self.monitor_thread = threading.Thread(
            target=self._monitor_loop,
            daemon=True,  # Auto-close when main program exits
            name="SystemMonitor"
        )
        self.monitor_thread.start()
        
        # Wait for first measurement
        time.sleep(self.check_interval * 2)
        print("🔍 System monitor started")
    
    def stop_monitoring(self):
        """Stop system monitoring"""
        if not self.is_monitoring:
            return
            
        self.is_monitoring = False
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=3.0)
        
        # Show statistics
        if self.monitor_start_time:
            uptime = time.time() - self.monitor_start_time
            print(f"\n🛑 System monitor stopped")
            print(f"   Total runtime: {uptime:.1f}s")
            print(f"   Total measurements: {self.total_measurements}")
            if self.total_throttle_time > 0:
                print(f"   Total throttle time: {self.total_throttle_time:.1f}s")
    
    def _monitor_loop(self):
        """Main monitoring loop - runs continuously in background"""
        while self.is_monitoring:
            try:
                # Collect system data
                cpu_percent = psutil.cpu_percent(interval=None)  # Non-blocking
                memory_info = psutil.virtual_memory()
                memory_percent = memory_info.percent
                
                # Thread-safe update
                with self.lock:
                    current_time = datetime.now()
                    
                    self.current_stats.update({
                        'cpu_percent': cpu_percent,
                        'memory_percent': memory_percent,
                        'memory_available_gb': memory_info.available / (1024**3),
                        'last_update': current_time,
                        'uptime_seconds': time.time() - self.monitor_start_time if self.monitor_start_time else 0
                    })
                    
                    # Update historical data
                    self.cpu_history.append(cpu_percent)
                    self.memory_history.append(memory_percent)
                    
                    # Update throttle status
                    self._update_throttle_status(cpu_percent, memory_percent)
                    
                    # Calculate recommended worker count
                    self._calculate_recommended_workers()
                    
                    self.total_measurements += 1
                
            except Exception as e:
                print(f"⚠️ System monitor error: {e}")
            
            time.sleep(self.check_interval)
    
    def _update_throttle_status(self, cpu_percent, memory_percent):
        """Update throttle status based on system usage"""
        cpu_threshold = THROTTLE_CPU_THRESHOLD
        memory_threshold = THROTTLE_MEMORY_THRESHOLD
        
        should_throttle = (cpu_percent > cpu_threshold or 
                          memory_percent > memory_threshold)
        
        if should_throttle and not self.throttle_active:
            # Throttle starting
            self.throttle_active = True
            self.throttle_start_time = time.time()
        
        elif not should_throttle and self.throttle_active:
            # Throttle ending
            if self.throttle_start_time:
                duration = time.time() - self.throttle_start_time
                self.total_throttle_time += duration
            self.throttle_active = False
        
        self.current_stats['should_throttle'] = should_throttle
    
    def _calculate_recommended_workers(self):
        """Calculate recommended worker count based on current system status"""
        cpu_percent = self.current_stats['cpu_percent']
        memory_percent = self.current_stats['memory_percent']
        cpu_count = self.current_stats['cpu_count']
        
        # Trend analysis (average of last 10 measurements)
        if len(self.cpu_history) >= 10:
            recent_cpu = list(self.cpu_history)[-10:]
            recent_memory = list(self.memory_history)[-10:]
            avg_cpu = sum(recent_cpu) / len(recent_cpu)
            avg_memory = sum(recent_memory) / len(recent_memory)
            
            # Trend calculation (is usage rising?)
            if len(recent_cpu) >= 5:
                cpu_trend = sum(recent_cpu[-3:]) / 3 - sum(recent_cpu[:3]) / 3
                memory_trend = sum(recent_memory[-3:]) / 3 - sum(recent_memory[:3]) / 3
            else:
                cpu_trend = memory_trend = 0
        else:
            avg_cpu = cpu_percent
            avg_memory = memory_percent
            cpu_trend = memory_trend = 0
        
        max_avg_usage = max(avg_cpu, avg_memory)
        
        # Dynamic worker calculation (including trend analysis)
        if max_avg_usage > 80 or max(cpu_trend, memory_trend) > 10:
            # Very high usage or rapidly rising trend
            workers = max(MIN_WORKERS, cpu_count // 2)
        elif max_avg_usage > 60 or max(cpu_trend, memory_trend) > 5:
            # Medium-high usage or moderately rising trend
            workers = max(MIN_WORKERS, int(cpu_count * 0.75))
        elif max_avg_usage > 40:
            # Medium usage - normal operation
            workers = cpu_count * MAX_WORKERS_MULTIPLIER
        elif max_avg_usage > 20:
            # Low usage - can handle more load
            workers = int(cpu_count * (MAX_WORKERS_MULTIPLIER + 0.5))
        else:
            # Very low usage - maximum performance
            workers = cpu_count * 3
        
        # Apply security limits
        workers = max(MIN_WORKERS, min(workers, MAX_WORKERS_LIMIT))
        
        self.current_stats['recommended_workers'] = workers
    
    def get_current_stats(self):
        """Get current system statistics (thread-safe)"""
        with self.lock:
            return self.current_stats.copy()
    
    def get_throttle_delay(self):
        """Calculate required throttle delay based on system load"""
        stats = self.get_current_stats()
        
        if not stats['should_throttle']:
            return 0.0
        
        cpu_percent = stats['cpu_percent']
        memory_percent = stats['memory_percent']
        max_usage = max(cpu_percent, memory_percent)
        
        # Progressive delay based on usage level
        if max_usage > 98:
            return 3.0  # Critical level - long delay
        elif max_usage > 95:
            return 2.0  # Very high level
        elif max_usage > 90:
            return 1.0  # High level  
        elif max_usage > 85:
            return 0.5  # Medium level
        else:
            return 0.2  # Light throttling
    
    def calculate_dynamic_batch_size(self, total_hosts, current_workers):
        """
        Calculate dynamic batch size based on system status
        
        Args:
            total_hosts (int): Total number of hosts to check
            current_workers (int): Current worker thread count
            
        Returns:
            int: Optimal batch size
        """
        stats = self.get_current_stats()
        cpu_percent = stats['cpu_percent']
        memory_percent = stats['memory_percent']
        
        # Base batch size (2-4 jobs per worker)
        base_batch = current_workers * 3
        
        # Adjust based on system load
        max_usage = max(cpu_percent, memory_percent)
        
        if max_usage > 85:
            # High load - very small batches
            multiplier = 0.4
        elif max_usage > 70:
            # Medium-high load - small batches
            multiplier = 0.7
        elif max_usage > 50:
            # Medium load - normal batches
            multiplier = 1.0
        elif max_usage > 30:
            # Low load - large batches
            multiplier = 1.4
        else:
            # Very low load - very large batches
            multiplier = 2.0
        
        # Additional adjustment based on memory pressure
        if memory_percent > 85:
            multiplier *= 0.8  # Reduce batch size if RAM is high
        
        dynamic_batch = int(base_batch * multiplier)
        
        # Apply reasonable limitations
        dynamic_batch = max(current_workers, dynamic_batch)  # At least equal to worker count
        dynamic_batch = min(total_hosts, dynamic_batch)      # No more than total hosts
        dynamic_batch = min(200, dynamic_batch)              # Maximum safety limit
        
        return dynamic_batch
    
    def print_realtime_stats(self):
        """Print real-time statistics in a single line format"""
        stats = self.get_current_stats()
        
        # Throttle status indicator
        throttle_emoji = "🔴" if stats['should_throttle'] else "🟢"
        
        # CPU and RAM progress bars
        cpu_bar = self._create_progress_bar(stats['cpu_percent'])
        ram_bar = self._create_progress_bar(stats['memory_percent'])
        
        print(f"\r💻 CPU:{cpu_bar}({stats['cpu_percent']:5.1f}%) | "
              f"RAM:{ram_bar}({stats['memory_percent']:5.1f}%) | "
              f"Workers:{stats['recommended_workers']:2d} | "
              f"Throttle:{throttle_emoji}", 
              end='', flush=True)
    
    def _create_progress_bar(self, percentage, width=8):
        """Create a small visual progress bar"""
        filled = int(width * percentage / 100)
        bar = "█" * filled + "░" * (width - filled)
        return bar
    
    def is_system_stable(self, stability_duration=5.0, variance_threshold=15.0):
        """
        Check if system has been stable for a certain duration
        
        Args:
            stability_duration (float): Required stability duration in seconds
            variance_threshold (float): Maximum acceptable variance percentage
            
        Returns:
            bool: True if system is stable
        """
        required_samples = int(stability_duration / self.check_interval)
        
        if len(self.cpu_history) < required_samples:
            return False
        
        # Check variance of recent measurements
        recent_cpu = list(self.cpu_history)[-required_samples:]
        recent_memory = list(self.memory_history)[-required_samples:]
        
        cpu_variance = max(recent_cpu) - min(recent_cpu)
        memory_variance = max(recent_memory) - min(recent_memory)
        
        # System is stable if variance is below threshold
        return (cpu_variance < variance_threshold and 
                memory_variance < variance_threshold)
    
    def get_system_health_summary(self):
        """Return comprehensive system health summary"""
        stats = self.get_current_stats()
        
        # CPU health assessment
        if stats['cpu_percent'] < 30:
            cpu_health = "Excellent"
        elif stats['cpu_percent'] < 60:
            cpu_health = "Good"
        elif stats['cpu_percent'] < 80:
            cpu_health = "Medium"
        else:
            cpu_health = "High"
        
        # Memory health assessment  
        if stats['memory_percent'] < 40:
            memory_health = "Excellent"
        elif stats['memory_percent'] < 70:
            memory_health = "Good"
        elif stats['memory_percent'] < 85:
            memory_health = "Medium"
        else:
            memory_health = "High"
        
        # Overall health determination
        if cpu_health in ['Excellent', 'Good'] and memory_health in ['Excellent', 'Good']:
            overall_health = 'Good'
        else:
            overall_health = 'Attention Required'
        
        return {
            'cpu_health': cpu_health,
            'memory_health': memory_health,
            'overall_health': overall_health,
            'is_stable': self.is_system_stable(),
            'throttle_active': stats['should_throttle'],
            'uptime': stats['uptime_seconds'],
            'cpu_percent': stats['cpu_percent'],
            'memory_percent': stats['memory_percent'],
            'recommended_workers': stats['recommended_workers']
        }
    
    def get_performance_recommendations(self):
        """Get performance optimization recommendations"""
        stats = self.get_current_stats()
        recommendations = []
        
        if stats['cpu_percent'] > 90:
            recommendations.append("⚠️ CPU usage is very high - consider reducing worker count")
        elif stats['cpu_percent'] < 20:
            recommendations.append("💡 CPU usage is low - you can increase worker count for faster processing")
        
        if stats['memory_percent'] > 85:
            recommendations.append("⚠️ Memory usage is high - consider reducing batch sizes")
        elif stats['memory_percent'] < 30:
            recommendations.append("💡 Memory usage is low - you can increase batch sizes")
        
        if self.total_throttle_time > 10:
            recommendations.append("📊 Frequent throttling detected - consider upgrading hardware")
        
        if not self.is_system_stable():
            recommendations.append("📈 System load is fluctuating - monitoring will auto-adjust performance")
        
        return recommendations
    
    def __enter__(self):
        """Context manager entry - start monitoring"""
        self.start_monitoring()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - stop monitoring"""
        self.stop_monitoring()
