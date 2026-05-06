"""Main entry point - run the log simulator"""

from log_generator.constants import Scenario, Intensity, Service
from simulator import LogSimulator


def main():
    """Demonstrate log generation with different scenarios"""
    
    print("\n" + "="*120)
    print("AI System Log Detection - Enhanced Training Data Generator")
    print("="*120 + "\n")
    
    # Create simulator
    sim = LogSimulator(seed=42)
    
    # Generate much more data for better training
    print("📊 Generating extensive training data...")
    
    # Normal operation - 4000 logs
    sim.generate_logs(4000, Scenario.NORMAL, Intensity.LOW)
    
    # Database latency scenarios - 3000 logs total
    sim.generate_logs(1000, Scenario.DB_LATENCY, Intensity.LOW)
    sim.generate_logs(1000, Scenario.DB_LATENCY, Intensity.MEDIUM) 
    sim.generate_logs(1000, Scenario.DB_LATENCY, Intensity.HIGH)
    
    # Auth failure scenarios - 3000 logs total
    sim.generate_logs(1000, Scenario.AUTH_FAILURE, Intensity.LOW)
    sim.generate_logs(1000, Scenario.AUTH_FAILURE, Intensity.MEDIUM)
    sim.generate_logs(1000, Scenario.AUTH_FAILURE, Intensity.HIGH)
    
    # Traffic spike scenarios - 3000 logs total
    sim.generate_logs(1000, Scenario.TRAFFIC_SPIKE, Intensity.LOW)
    sim.generate_logs(1000, Scenario.TRAFFIC_SPIKE, Intensity.MEDIUM)
    sim.generate_logs(1000, Scenario.TRAFFIC_SPIKE, Intensity.HIGH)
    
    # System degradation scenarios - 3000 logs total
    sim.generate_logs(1000, Scenario.DEGRADATION, Intensity.LOW)
    sim.generate_logs(1000, Scenario.DEGRADATION, Intensity.MEDIUM)
    sim.generate_logs(1000, Scenario.DEGRADATION, Intensity.HIGH)
    
    # Export all logs
    sim.export_jsonl("logs.jsonl")
    
    print(f"\n✅ Total logs generated: {len(sim.logs)}")
    print(f"📁 Output saved to logs.jsonl\n")
    
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
