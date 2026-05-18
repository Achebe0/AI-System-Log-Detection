import time
from .monitor import Monitor
from .reasoning import Reasoner
from .action import Executor


class LogAgent:
    """
    Main agent - orchestrates perception → reasoning → action loop
    """
    
    def __init__(self, jsonl_file: str):
        self.monitor = Monitor(jsonl_file)
        self.reasoner = Reasoner()
        self.executor = Executor()
        
        # Timing metrics
        self.latencies = []  # Track latency per log
        
        # Connect perception to reasoning via callback
        self.monitor.register_callback(self._on_log_perceived)
    
    def _on_log_perceived(self, log_event):
        """Calls back when a new log is perceived -> action and reasoning happens"""
        start = time.time()
        
        # REASON about the log
        analysis = self.reasoner.reason_about_log(log_event)
        
        # ACT based on analysis
        self.executor.execute_action(analysis)
        
        # Record latency
        latency_ms = (time.time() - start) * 1000
        self.latencies.append(latency_ms)
    
    def run(self, duration_seconds: int = 10, poll_interval: float = 0.5):
        
        "Main loop"
        print("\n" + "="*70)
        print("AGENTIC LOG DETECTOR - ACTIVATED")
        print("="*70)
        print(f"Monitoring: {self.monitor.json_file}")
        print(f"Poll interval: {poll_interval}s\n")
        
        start_time = time.time()
        
        while (time.time() - start_time) < duration_seconds:
            # PERCEIVE: Check for new logs
            new_logs = self.monitor.check_for_new_logs()
            
            if new_logs:
                print(f"[{len(new_logs)} logs processed]")
            
            time.sleep(poll_interval)
        
        # Print summary
        self._print_summary()
    
    def _print_summary(self):
        """Print final report"""
        print("\n" + "="*70)
        print(" AGENT SUMMARY")
        print("="*70)
        print(f"Logs perceived: {self.monitor.logs_seen}")
        print(f"Decisions made: {self.reasoner.decisions_made}")
        print(self.executor.get_summary())
        
        # Performance metrics
        if self.latencies:
            avg_latency = sum(self.latencies) / len(self.latencies)
            min_latency = min(self.latencies)
            max_latency = max(self.latencies)
            print(f"\n  Performance Metrics:")
            print(f"  - Min latency: {min_latency:.2f}ms")
            print(f"  - Max latency: {max_latency:.2f}ms")
            print(f"  - Avg latency: {avg_latency:.2f}ms")
            print(f"  - Throughput: {1000/avg_latency:.0f} logs/sec")
        
        print("="*70 + "\n")


if __name__ == "__main__":
    agent = LogAgent("logs.jsonl")
    agent.run(duration_seconds=5, poll_interval=0.5)