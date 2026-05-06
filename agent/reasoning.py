from .models import LogEvent, KowalskiAnalysis, Anamoly_Lvl


class Reasoner:
    
    
    def __init__(self):
        self.decisions_made = 0
    
    def reason_about_log(self, log_event: LogEvent) -> KowalskiAnalysis:
        """
        Apply logic to classify the log event
        Returns: KowalskiAnalysis with decision + confidence
        """
        self.decisions_made += 1
        
        # Rule-based classification logic
        anomaly_level, confidence, reasoning = self._classify(log_event)
        
        analysis = KowalskiAnalysis(
            log_event=log_event,
            anamoly_level=anomaly_level,
            confidence=confidence,
            reasoning=reasoning
        )
        
        return analysis
    
    def _classify(self, log: LogEvent) -> tuple:
        """
        Apply heuristic rules to classify the log
        Returns: (anomaly_level, confidence, reasoning)
        """
        
        # CRITICAL: Server errors + high latency = big problem
        if log.status_code >= 500:
            return (
                Anamoly_Lvl.CRITICAL,
                0.95,
                f"Server error (status {log.status_code})"
            )
        
        # CRITICAL: High latency + error status
        if log.latency_ms > 2000 and log.status_code >= 400:
            return (
                Anamoly_Lvl.CRITICAL,
                0.90,
                f"High latency ({log.latency_ms}ms) + error status ({log.status_code})"
            )
        
        # CRITICAL: Explicit severity flag
        if log.severity == "CRITICAL":
            return (
                Anamoly_Lvl.CRITICAL,
                0.92,
                f"Marked as CRITICAL: {log.msg}"
            )
        
        # MEDIUM: Client errors or moderate latency
        if log.status_code >= 400:
            return (
                Anamoly_Lvl.MEDIUM,
                0.75,
                f"Client/server error (status {log.status_code})"
            )
        
        # MEDIUM: High latency
        if log.latency_ms > 1000:
            return (
                Anamoly_Lvl.MEDIUM,
                0.70,
                f"High latency detected ({log.latency_ms}ms)"
            )
        
        # MEDIUM: Warning severity
        if log.severity == "WARNING" or log.severity == "ERROR":
            return (
                Anamoly_Lvl.MEDIUM,
                0.65,
                f"Severity {log.severity}: {log.msg}"
            )
        
        # NORMAL: All good
        return (
            Anamoly_Lvl.NORMAL,
            0.95,
            "System operating normally"
        )