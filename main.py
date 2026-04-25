"""Main entry point - run the log simulator"""

from log_generator.constants import Scenario, Intensity, Service
from simulator import LogSimulator


def main():
    """Demonstrate log generation with different scenarios"""
    
    print("\n" + "="*120)
    print("AI System Log Detection - MVP Log Simulator")
    print("="*120 + "\n")
    
    # Create simulator
    sim = LogSimulator(seed=42)
    
    # Scenario 1: Normal Operation 
    print("📊 Generating 30 NORMAL logs...")
    sim.generate_logs(30, Scenario.NORMAL, Intensity.LOW)
    sim.print_logs(5)
    
    #  Scenario 2: Database Latency (MEDIUM) 
    print("\n\n📊 Generating 30 logs with DB_LATENCY (MEDIUM intensity)...")
    sim.generate_logs(30, Scenario.DB_LATENCY, Intensity.MEDIUM)
    sim.print_logs(5)
    
    #  Scenario 3: Auth Failures (HIGH) 
    print("\n\n📊 Generating 30 logs with AUTH_FAILURE (HIGH intensity)...")
    sim.generate_logs(30, Scenario.AUTH_FAILURE, Intensity.HIGH)
    sim.print_logs(5)
    
    #  Scenario 4: Traffic Spike (HIGH) 
    print("\n\n📊 Generating 30 logs with TRAFFIC_SPIKE (HIGH intensity)...")
    sim.generate_logs(30, Scenario.TRAFFIC_SPIKE, Intensity.HIGH)
    sim.print_logs(5)
    
    #  Scenario 5: System Degradation (HIGH) 
    print("\n\n📊 Generating 30 logs with DEGRADATION (HIGH intensity)...")
    sim.generate_logs(30, Scenario.DEGRADATION, Intensity.HIGH)
    sim.print_logs(5)
    
    # Export all logs
    sim.export_jsonl("logs.jsonl")
    
    print(f"\n✅ Total logs generated: {len(sim.logs)}")
    print(f"📁 Output saved to logs.jsonl\n")
    
    print("\n" + "="*120)
    print("🤖 AI Incident Reporter (Cohere)")
    print("="*120 + "\n")
    
    try:
        from Cohere_Client.client import IncidentSummarizer
        summarizer = IncidentSummarizer()
        
        # Grab only anomalous logs that are ERROR or CRITICAL
        # Depending on how the object is structured severity might be a string or an Enum
        anomalies = []
        for log in sim.logs:
            sev = log.severity.value if hasattr(log.severity, 'value') else log.severity
            if sev in ["ERROR", "CRITICAL"]:
                anomalies.append(log.to_dict() if hasattr(log, 'to_dict') else log.__dict__)
        
        if anomalies:
            print(f"Detected {len(anomalies)} critical anomalies. Generating incident report...")
            report = summarizer.summarize_logs(anomalies)
            print("\n🚨 INCIDENT REPORT 🚨")
            print("-" * 50)
            print(report)
            print("\n" + "="*120)
        else:
            print("No critical anomalies found to summarize.")
    except Exception as e:
        print(f"Cohere Client could not summarize the logs. Is the API key set?\nError: {e}")

if __name__ == "__main__":
    main()
