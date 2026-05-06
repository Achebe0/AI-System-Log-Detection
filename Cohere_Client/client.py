import cohere
from config.settings import COHERE_API_KEY, COHERE_MODEL


class SummarizeIncident:
    def __init__ (self):
        if not COHERE_API_KEY or COHERE_API_KEY == "your_cohere_api_key_here":
            raise ValueError("Invalid Cohere API Key. Please update your .env file.")
        
        self.client = cohere.Client(COHERE_API_KEY)

      # takes a list of log incidents and uses the Cohere Command R model to summarize them  
    def summarize_logs(self, anomaly_logs):
      
        if not anomaly_logs:
            return "No anomalies detected, clean system!"
            
        logs_str = "\n".join([str(log) for log in anomaly_logs[:50]]) # Limit to 50 to save tokens
        
        prompt = f"""You are an expert DevOps AI assistant. Review the following system anomaly logs and provide a concise incident summary (2-3 sentences).
Point out the likely root cause and affected services.

Logs:
{logs_str}"""
        
        response = self.client.chat(
            model=COHERE_MODEL,
            message=prompt,
            max_tokens=200,
            temperature=0.3,
        )
        
        return response.text.strip()

if __name__ == "__main__":
    # Example usage:
    sample_logs = [
        {"timestamp": "2026-04-25T10:00:01", "service": "database_service", "severity": "ERROR", "message": "Connection Timeout"},
        {"timestamp": "2026-04-25T10:00:02", "service": "api_service", "severity": "WARNING", "message": "High latency detected"}
    ]
    
    try:
        summarizer = SummarizeIncident()
        report = summarizer.summarize_logs(sample_logs)
        print(" Generated Incident Report:")
        print(report)
    except Exception as e:
        print(f"Error: {e}")
