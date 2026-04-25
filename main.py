"""Main entry point - run the log simulator"""

from constants import Scenario, Intensity, Service
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


if __name__ == "__main__":
    main()
