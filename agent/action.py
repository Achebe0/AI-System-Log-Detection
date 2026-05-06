from .models import KowalskiAnalysis, Action, Anamoly_Lvl


class Executor:
   
    
    def __init__(self):
        self.actions_taken = []
        self.alerts_sent = 0
        self.escalations = 0
    
    def execute_action(self, analysis: KowalskiAnalysis) -> Action:
        """
        Given an analysis, take appropriate action
        Returns: Action object describing what was done
        """
        
        # Decision logic
        if analysis.anamoly_level == Anamoly_Lvl.CRITICAL:
            action = self._escalate_incident(analysis)
        elif analysis.anamoly_level == Anamoly_Lvl.MEDIUM:
            action = self._send_alert(analysis)
        else:
            action = self._log_event(analysis)
        
        self.actions_taken.append(action)
        return action
    
    def _escalate_incident(self, analysis: KowalskiAnalysis) -> Action:
        """Critical level - escalate to on-call engineer"""
        log = analysis.log_event
        msg = f"🚨 CRITICAL: {analysis.reasoning}"
        
        print(f"\n{msg}")
        print(f"   Service: {log.service}")
        print(f"   Confidence: {analysis.confidence:.0%}")
        
        # Try to generate AI summary for critical incidents
        summary = self._generate_incident_summary(log)
        if summary:
            print(f"   📋 Summary: {summary}")
        
        print(f"   → Alerting on-call engineer...")
        
        self.escalations += 1
        
        # Include summary in description if available
        full_desc = msg + (f"\n{summary}" if summary else "")
        
        return Action(
            action_type="ESCALATE",
            target=log.service,
            desc=full_desc,
            severity="CRITICAL"
        )
    
    def _generate_incident_summary(self, log) -> str:
        """Optional: Generate AI summary for critical incident"""
        try:
            from Cohere_Client.client import IncidentSummarizer
            summarizer = IncidentSummarizer()
            
            # Create log dict for Cohere
            log_dict = {
                "timestamp": log.timestamp,
                "service": log.service,
                "latency_ms": log.latency_ms,
                "status_code": log.status_code,
                "severity": log.severity,
                "message": log.msg,
                "scenario": log.scenario
            }
            
            summary = summarizer.summarize_logs([log_dict])
            return summary
        except Exception as e:
            # Gracefully fail - Cohere not configured or API error
            # Agent still works without it
            return None
    
    def _send_alert(self, analysis: KowalskiAnalysis) -> Action:
        
        "Medium lvl, this sends an alert to the dashboard just to keep the engineers wary"
        log = analysis.log_event
        msg = f"⚠️  ALERT: {analysis.reasoning}"
        
        print(f"\n{msg}")
        print(f"   Service: {log.service}")
        print(f"   Confidence: {analysis.confidence:.0%}")
        
        self.alerts_sent += 1
        
        return Action(
            action_type="ALERT",
            target=log.service,
            desc=msg,
            severity="WARNING"
        )
    
    def _log_event(self, analysis: KowalskiAnalysis) -> Action:
        
        "No need to stress the engineers for now"
        log = analysis.log_event
        msg = f"✓ NORMAL: {analysis.reasoning}"
        
        return Action(
            action_type="LOG",
            target=log.service,
            desc=msg,
            severity="INFO"
        )
    
    def get_summary(self) -> str:

        ## Written by AI below
        """Report on actions taken"""
        return f"""
Action Summary:
  - Total actions: {len(self.actions_taken)}
  - Alerts sent: {self.alerts_sent}
  - Escalations: {self.escalations}
"""