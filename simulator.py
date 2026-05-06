"""Log simulator - generates logs based on scenarios"""

import random
from datetime import datetime, timedelta
from log_generator.constants import Service, Scenario, Intensity, Severity
from log_generator.log_entry import LogEntry


class LogSimulator:
    """Generates synthetic logs for different services and anomaly scenarios"""
    
    def __init__(self, seed: int = 42):
        random.seed(seed)
        self.current_time = datetime(2026, 4, 25, 10, 0, 0)
        self.logs = []
    
    def _get_normal_latency(self, service: Service) -> int:
        """Baseline latency for each service"""
        baseline = {
            Service.AUTH: random.randint(40, 80),
            Service.DATABASE: random.randint(50, 150),
            Service.API: random.randint(80, 200)
        }
        return baseline[service]
    
    def _get_normal_status(self, service: Service) -> int:
        """Baseline status code - 99% success"""
        if random.random() < 0.99:
            return 200
        return random.choice([400, 401, 403, 500])
    
    def _apply_scenario_effects(self, 
                               service: Service, 
                               scenario: Scenario, 
                               intensity: Intensity) -> tuple:
        """Apply scenario modifications: (latency_mod, status_override, severity, message)"""
        
        if scenario == Scenario.NORMAL:
            return (0, None, Severity.INFO, "Normal operation")
        
        elif scenario == Scenario.DB_LATENCY:
            # Apply to ALL services for more distinct patterns
            latency_mod = {
                Intensity.LOW: 300,
                Intensity.MEDIUM: 800,
                Intensity.HIGH: 2500
            }[intensity]
            return (latency_mod, None, Severity.WARNING, "High latency detected")
        
        elif scenario == Scenario.AUTH_FAILURE:
            # Apply to ALL services - high error rates
            error_rate = {
                Intensity.LOW: 0.15,
                Intensity.MEDIUM: 0.40,
                Intensity.HIGH: 0.75
            }[intensity]
            
            if random.random() < error_rate:
                return (50, random.choice([401, 403, 500]), Severity.ERROR, "Access denied")
            return (0, None, Severity.INFO, "Request successful")
        
        elif scenario == Scenario.TRAFFIC_SPIKE:
            # Apply to ALL services - very high latency
            latency_mod = {
                Intensity.LOW: 200,
                Intensity.MEDIUM: 600,
                Intensity.HIGH: 1500
            }[intensity]
            
            # High intensity may cause 429 errors
            if intensity == Intensity.HIGH and random.random() < 0.25:
                return (latency_mod, 429, Severity.ERROR, "Too many requests")
            
            return (latency_mod, None, Severity.WARNING, "High load")
        
        elif scenario == Scenario.DEGRADATION:
            # Apply to ALL services - moderate latency increase with occasional errors
            degradation = {
                Intensity.LOW: 150,
                Intensity.MEDIUM: 400,
                Intensity.HIGH: 1000
            }[intensity]
            
            # Occasional errors during degradation
            if random.random() < 0.10 * intensity.value:
                return (degradation, random.choice([500, 502, 503]), Severity.ERROR, "Service unavailable")
            
            return (degradation, None, Severity.WARNING, "Performance degradation")
        
        return (0, None, Severity.INFO, "Unknown scenario")
    
    def generate_logs(self, 
                     num_logs: int,
                     scenario: Scenario,
                     intensity: Intensity,
                     logs_per_service: dict = None) -> list:
        """
        Generate synthetic logs
        
        Args:
            num_logs: Total number of logs to generate
            scenario: Current anomaly scenario
            intensity: Intensity level (LOW, MEDIUM, HIGH)
            logs_per_service: Override logs per service (e.g. {Service.API: 20})
        
        Returns:
            List of LogEntry objects
        """
        
        if logs_per_service is None:
            # Default: 10 logs per service per call
            logs_per_service = {
                Service.AUTH: max(1, num_logs // 3),
                Service.DATABASE: max(1, num_logs // 3),
                Service.API: max(1, num_logs // 3)
            }
        
        generated_logs = []
        
        for service, count in logs_per_service.items():
            for _ in range(count):
                # Base latency
                latency = self._get_normal_latency(service)
                status = self._get_normal_status(service)
                severity = Severity.INFO
                message = "Request processed"
                
                # Apply scenario effects
                latency_mod, status_override, sev, msg = self._apply_scenario_effects(
                    service, scenario, intensity
                )
                
                latency += latency_mod
                if status_override is not None:
                    status = status_override
                severity = sev
                message = msg
                
                # Create log entry
                log = LogEntry(
                    timestamp=self.current_time.isoformat(),
                    service=service.value,
                    latency_ms=latency,
                    status_code=status,
                    severity=severity.value,
                    message=message,
                    scenario=scenario.value
                )
                
                generated_logs.append(log)
                self.current_time += timedelta(milliseconds=random.randint(10, 50))
        
        self.logs.extend(generated_logs)
        return generated_logs
    
    def export_jsonl(self, filename: str) -> None:
        """Export all logs to JSONL file"""
        with open(filename, 'w') as f:
            for log in self.logs:
                f.write(log.to_jsonl() + '\n')
        print(f"✅ Exported {len(self.logs)} logs to {filename}")
    
    def print_logs(self, count: int = 10) -> None:
        """Print first N logs"""
        print(f"\n{'='*120}")
        print(f"Sample Logs (first {min(count, len(self.logs))} of {len(self.logs)})")
        print(f"{'='*120}\n")
        
        for log in self.logs[:count]:
            print(f"[{log.timestamp}] {log.service:15} | "
                  f"Status: {log.status_code} | "
                  f"Latency: {log.latency_ms:4}ms | "
                  f"{log.severity:8} | "
                  f"{log.message}")
