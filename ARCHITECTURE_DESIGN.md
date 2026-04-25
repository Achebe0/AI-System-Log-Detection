# Controlled Log Generation System Architecture

A production-grade architecture for generating realistic, controlled logs from simulated microservices for AI anomaly detection training.

---

## 1. Folder Structure

```
AI-System-Log-Detection/
│
├── simulation/                          # Core simulation engine
│   ├── __init__.py
│   ├── engine.py                       # SimulationEngine - orchestrates everything
│   ├── clock.py                        # SimulationClock - deterministic time progression
│   └── state.py                        # GlobalState - shared system state
│
├── services/                            # Microservice definitions
│   ├── __init__.py
│   ├── base_service.py                 # BaseService abstract class
│   ├── auth_service.py                 # AuthService implementation
│   ├── database_service.py             # DatabaseService implementation
│   ├── api_service.py                  # APIService implementation
│   └── service_manager.py              # ServiceManager - manages all services
│
├── scenarios/                           # Anomaly scenario definitions
│   ├── __init__.py
│   ├── base_scenario.py                # BaseScenario abstract class
│   ├── scenario_normal.py              # NormalScenario
│   ├── scenario_db_latency.py          # DatabaseLatencyScenario
│   ├── scenario_auth_failure.py        # AuthFailureScenario
│   ├── scenario_traffic_spike.py       # TrafficSpikeScenario
│   ├── scenario_degradation.py         # SystemDegradationScenario
│   └── scenario_manager.py             # ScenarioManager - transitions scenarios
│
├── controller/                          # Central orchestration
│   ├── __init__.py
│   └── system_controller.py            # SystemController - manages transitions & state
│
├── logging/                             # Structured logging system
│   ├── __init__.py
│   ├── log_manager.py                  # LoggingManager - standardizes logging
│   ├── log_formatter.py                # LogFormatter - formats logs to JSONL
│   ├── log_models.py                   # LogEntry, LogMetadata data classes
│   └── log_writer.py                   # LogWriter - writes to console/file
│
├── utils/                               # Utilities
│   ├── __init__.py
│   ├── constants.py                    # Enums: Severity, Scenario, ServiceType
│   ├── metrics.py                      # MetricsCollector - tracks performance
│   └── validators.py                   # InputValidator - validates configurations
│
├── config.py                            # Configuration management
└── simulation_runner.py                 # Entry point - runs simulation

```

---

## 2. Class Design & Responsibilities

### 2.1 Core Simulation Layer

#### **SimulationEngine**
**File:** `simulation/engine.py`

**Responsibility:** Main orchestrator that runs the complete simulation loop

**Pseudo-interface:**
```python
class SimulationEngine:
    """
    Orchestrates entire simulation lifecycle.
    
    Responsibilities:
    - Initialize simulation with config
    - Run main event loop
    - Coordinate services, controller, scenarios
    - Ensure deterministic execution
    - Track global metrics
    """
    
    def __init__(self, config: SimulationConfig) -> None:
        """Initialize with configuration."""
        pass
    
    def initialize_system(self) -> None:
        """Setup all services, controller, and scenarios."""
        pass
    
    def run(self, duration_seconds: int) -> SimulationResults:
        """Run simulation for specified duration."""
        pass
    
    def step(self) -> None:
        """Execute one simulation step (deterministic)."""
        pass
    
    def shutdown(self) -> None:
        """Gracefully shutdown all services."""
        pass
    
    def get_current_state(self) -> SystemState:
        """Get complete current system state."""
        pass
```

**What it coordinates:**
- ServiceManager (all services)
- SystemController (scenario transitions)
- SimulationClock (time progression)
- LoggingManager (log collection)
- ScenarioManager (scenario scheduling)

---

#### **SimulationClock**
**File:** `simulation/clock.py`

**Responsibility:** Deterministic time progression for reproducible simulations

**Pseudo-interface:**
```python
class SimulationClock:
    """
    Manages deterministic time in simulation.
    
    Responsibilities:
    - Provide consistent time across all components
    - Support time skipping (accelerated simulation)
    - Enable deterministic seeding
    """
    
    def __init__(self, start_time: datetime, seed: int = None) -> None:
        """Initialize with optional seed for reproducibility."""
        pass
    
    def current_time(self) -> datetime:
        """Get current simulation time."""
        pass
    
    def advance(self, seconds: float) -> None:
        """Advance time by specified seconds."""
        pass
    
    def set_speed_multiplier(self, multiplier: float) -> None:
        """1.0 = real-time, 10.0 = 10x speed."""
        pass
    
    def get_seed(self) -> int:
        """Get current seed for reproducibility."""
        pass
```

---

#### **GlobalState**
**File:** `simulation/state.py`

**Responsibility:** Shared system state accessible to all components

**Pseudo-interface:**
```python
class GlobalState:
    """
    Maintains shared system state.
    
    Responsibilities:
    - Store service health metrics
    - Track current scenario
    - Manage resource utilization
    - Support state queries and updates
    """
    
    def __init__(self) -> None:
        """Initialize with default state."""
        pass
    
    def set_service_health(self, service: str, health: float) -> None:
        """Set health score (0.0-1.0) for service."""
        pass
    
    def get_service_health(self, service: str) -> float:
        """Retrieve service health score."""
        pass
    
    def set_current_scenario(self, scenario: ScenarioType, intensity: IntensityLevel) -> None:
        """Update active scenario and intensity."""
        pass
    
    def get_current_scenario(self) -> tuple[ScenarioType, IntensityLevel]:
        """Get active scenario info."""
        pass
    
    def set_resource_metrics(self, cpu: float, memory: float, disk: float) -> None:
        """Update resource utilization (0.0-1.0)."""
        pass
    
    def get_resource_metrics(self) -> ResourceMetrics:
        """Get current resource state."""
        pass
    
    def increment_request_count(self, service: str) -> None:
        """Track request volumes."""
        pass
    
    def add_state_observer(self, callback: Callable) -> None:
        """Subscribe to state changes."""
        pass
```

---

### 2.2 Service Layer

#### **BaseService (Abstract)**
**File:** `services/base_service.py`

**Responsibility:** Define interface all services must implement

**Pseudo-interface:**
```python
class BaseService(ABC):
    """
    Abstract base for all microservices.
    
    Responsibilities:
    - Define common service lifecycle
    - Provide logging interface
    - Handle scenario effects
    - Track health metrics
    """
    
    def __init__(self, name: str, logging_manager: LoggingManager) -> None:
        """Initialize service with logger."""
        pass
    
    @abstractmethod
    def initialize(self) -> None:
        """Startup service resources."""
        pass
    
    @abstractmethod
    def shutdown(self) -> None:
        """Cleanup service resources."""
        pass
    
    @abstractmethod
    def process_request(self, request: ServiceRequest) -> ServiceResponse:
        """Handle incoming request (main work)."""
        pass
    
    @abstractmethod
    def apply_scenario_effect(self, scenario: ScenarioType, intensity: IntensityLevel) -> None:
        """Modify service behavior based on active scenario."""
        pass
    
    def log_event(self, severity: Severity, message: str, metadata: dict = None) -> None:
        """Log event through manager."""
        pass
    
    def get_health_status(self) -> HealthStatus:
        """Return service health metrics."""
        pass
    
    @abstractmethod
    def reset_scenario_effects(self) -> None:
        """Return to normal behavior when scenario ends."""
        pass
```

---

#### **AuthService**
**File:** `services/auth_service.py`

**Responsibility:** Simulate authentication service

**Pseudo-interface:**
```python
class AuthService(BaseService):
    """
    Simulates user authentication service.
    
    Logs Generated:
    - INFO: Successful login/logout
    - WARNING: Multiple failed attempts
    - ERROR: Invalid credentials, service timeouts
    
    Scenario Effects:
    - AUTH_FAILURE: Increases rejection rate
    - TRAFFIC_SPIKE: Increased latency
    - SYSTEM_DEGRADATION: Random service disruptions
    """
    
    def initialize(self) -> None:
        """Setup auth database connection pool."""
        pass
    
    def shutdown(self) -> None:
        """Close connections."""
        pass
    
    def process_request(self, request: AuthRequest) -> AuthResponse:
        """
        Validate credentials, return auth token.
        
        Flow:
        1. Check request format
        2. Query user database
        3. Verify password
        4. Generate token
        5. Log result
        """
        pass
    
    def apply_scenario_effect(self, scenario: ScenarioType, intensity: IntensityLevel) -> None:
        """
        Modify behavior based on scenario:
        - HIGH intensity AUTH_FAILURE: 50% rejection rate
        - MEDIUM: 20% rejection rate
        - LOW: 5% rejection rate
        """
        pass
    
    def reset_scenario_effects(self) -> None:
        """Return to normal 99% success rate."""
        pass
```

---

#### **DatabaseService**
**File:** `services/database_service.py`

**Responsibility:** Simulate database operations

**Pseudo-interface:**
```python
class DatabaseService(BaseService):
    """
    Simulates database service (PostgreSQL-like).
    
    Logs Generated:
    - INFO: Query execution, connection pooling
    - WARNING: Slow queries (>500ms), high memory
    - ERROR: Connection timeouts, deadlocks, out of memory
    
    Scenario Effects:
    - DB_LATENCY: Increases query response time
    - TRAFFIC_SPIKE: Connection pool exhaustion
    - SYSTEM_DEGRADATION: Random failures
    """
    
    def initialize(self) -> None:
        """Setup connection pool, in-memory dataset."""
        pass
    
    def shutdown(self) -> None:
        """Close connections."""
        pass
    
    def process_request(self, request: DatabaseQuery) -> QueryResult:
        """
        Execute database query.
        
        Flow:
        1. Acquire connection from pool
        2. Parse query
        3. Simulate execution with latency
        4. Return results
        5. Log performance metrics
        """
        pass
    
    def apply_scenario_effect(self, scenario: ScenarioType, intensity: IntensityLevel) -> None:
        """
        Modify behavior:
        - DB_LATENCY HIGH: Add 2000ms to all queries
        - DB_LATENCY MEDIUM: Add 500ms
        - TRAFFIC_SPIKE: Increase connection pool contention
        """
        pass
    
    def reset_scenario_effects(self) -> None:
        """Return to baseline latency (50-100ms)."""
        pass
```

---

#### **APIService**
**File:** `services/api_service.py`

**Responsibility:** Simulate REST API gateway

**Pseudo-interface:**
```python
class APIService(BaseService):
    """
    Simulates API gateway/REST endpoint.
    
    Logs Generated:
    - INFO: Request received, response sent
    - WARNING: Slow responses (>1000ms)
    - ERROR: 5xx errors, rate limit exceeded
    
    Scenario Effects:
    - TRAFFIC_SPIKE: Increased request volume, slower responses
    - SYSTEM_DEGRADATION: Increased error rates
    """
    
    def initialize(self) -> None:
        """Setup request queue, rate limiters."""
        pass
    
    def shutdown(self) -> None:
        """Flush queued requests."""
        pass
    
    def process_request(self, request: HTTPRequest) -> HTTPResponse:
        """
        Handle API request.
        
        Flow:
        1. Accept request
        2. Route to appropriate service
        3. Call downstream services
        4. Aggregate response
        5. Return to client
        6. Log request/response
        """
        pass
    
    def apply_scenario_effect(self, scenario: ScenarioType, intensity: IntensityLevel) -> None:
        """
        Modify behavior:
        - TRAFFIC_SPIKE HIGH: 10x request volume
        - TRAFFIC_SPIKE MEDIUM: 3x request volume
        """
        pass
    
    def reset_scenario_effects(self) -> None:
        """Return to baseline request rate."""
        pass
```

---

#### **ServiceManager**
**File:** `services/service_manager.py`

**Responsibility:** Manages all service instances

**Pseudo-interface:**
```python
class ServiceManager:
    """
    Manages collection of all services.
    
    Responsibilities:
    - Instantiate and lifecycle all services
    - Route requests to appropriate services
    - Coordinate inter-service communication
    """
    
    def __init__(self, logging_manager: LoggingManager) -> None:
        """Initialize with logger."""
        pass
    
    def create_services(self) -> None:
        """Instantiate all service instances."""
        pass
    
    def get_service(self, service_type: ServiceType) -> BaseService:
        """Retrieve service by type."""
        pass
    
    def execute_request(self, request: ServiceRequest) -> ServiceResponse:
        """Route request to appropriate service."""
        pass
    
    def initialize_all(self) -> None:
        """Startup all services."""
        pass
    
    def shutdown_all(self) -> None:
        """Gracefully shutdown all services."""
        pass
    
    def apply_scenario_to_all(self, scenario: ScenarioType, intensity: IntensityLevel) -> None:
        """Apply scenario effect to all affected services."""
        pass
    
    def reset_all_scenarios(self) -> None:
        """Reset all services to normal state."""
        pass
    
    def get_all_health_statuses(self) -> dict[str, HealthStatus]:
        """Get health metrics for all services."""
        pass
```

---

### 2.3 Scenario System

#### **BaseScenario (Abstract)**
**File:** `scenarios/base_scenario.py`

**Responsibility:** Define scenario interface

**Pseudo-interface:**
```python
class BaseScenario(ABC):
    """
    Abstract base for all anomaly scenarios.
    
    Responsibilities:
    - Define scenario lifecycle
    - Specify affected services
    - Control intensity levels
    """
    
    def __init__(self, name: str, intensity: IntensityLevel = IntensityLevel.MEDIUM) -> None:
        """Initialize scenario with intensity."""
        pass
    
    @abstractmethod
    def get_affected_services(self) -> list[ServiceType]:
        """Return which services are affected."""
        pass
    
    @abstractmethod
    def activate(self, service_manager: ServiceManager, global_state: GlobalState) -> None:
        """Apply scenario effects when activated."""
        pass
    
    @abstractmethod
    def deactivate(self, service_manager: ServiceManager, global_state: GlobalState) -> None:
        """Remove scenario effects when deactivated."""
        pass
    
    def set_intensity(self, intensity: IntensityLevel) -> None:
        """Update scenario intensity (LOW, MEDIUM, HIGH)."""
        pass
    
    def get_description(self) -> str:
        """Human-readable scenario description."""
        pass
```

---

#### **NormalScenario**
**File:** `scenarios/scenario_normal.py`

**Responsibility:** Baseline healthy system operation

**Pseudo-interface:**
```python
class NormalScenario(BaseScenario):
    """
    Baseline scenario - all systems healthy.
    
    Characteristics:
    - All services: ~99.9% success rate
    - Response times: 50-200ms
    - CPU: 20-40%
    - Memory: 40-60%
    - Logs: Mostly INFO and occasional WARNING
    - Error rate: <0.1%
    """
    
    def get_affected_services(self) -> list[ServiceType]:
        """No services affected - baseline."""
        pass
    
    def activate(self, service_manager, global_state) -> None:
        """Set all services to normal parameters."""
        pass
    
    def deactivate(self, service_manager, global_state) -> None:
        """No-op for normal scenario."""
        pass
```

---

#### **DatabaseLatencyScenario**
**File:** `scenarios/scenario_db_latency.py`

**Responsibility:** Database performance degradation

**Pseudo-interface:**
```python
class DatabaseLatencyScenario(BaseScenario):
    """
    Database latency anomaly.
    
    Affected Services:
    - DatabaseService (primary)
    - APIService (secondary - slow responses)
    - AuthService (secondary - if auth queries slow)
    
    Intensity Effects:
    - LOW: Query latency +200ms, CPU +10%
    - MEDIUM: Query latency +500ms, CPU +20%, occasional timeouts
    - HIGH: Query latency +2000ms, CPU +40%, 5% timeout rate
    
    Logs Generated:
    - WARNING: Slow query (>500ms)
    - ERROR: Query timeout, connection pool exhaustion
    """
    
    def get_affected_services(self) -> list[ServiceType]:
        """DatabaseService, APIService, AuthService."""
        pass
    
    def activate(self, service_manager, global_state) -> None:
        """Increase database latency based on intensity."""
        pass
    
    def deactivate(self, service_manager, global_state) -> None:
        """Return to normal latency."""
        pass
```

---

#### **AuthFailureScenario**
**File:** `scenarios/scenario_auth_failure.py`

**Responsibility:** Authentication system failures

**Pseudo-interface:**
```python
class AuthFailureScenario(BaseScenario):
    """
    Authentication service failures.
    
    Affected Services:
    - AuthService (primary)
    - APIService (secondary - 4xx errors)
    
    Intensity Effects:
    - LOW: 5% auth rejection rate
    - MEDIUM: 20% auth rejection rate
    - HIGH: 50% auth rejection rate, intermittent service unavailability
    
    Logs Generated:
    - ERROR: Invalid credentials, service unavailable
    - WARNING: High failed auth attempt rate
    """
    
    def get_affected_services(self) -> list[ServiceType]:
        """AuthService, APIService."""
        pass
    
    def activate(self, service_manager, global_state) -> None:
        """Increase auth failure rate based on intensity."""
        pass
    
    def deactivate(self, service_manager, global_state) -> None:
        """Return to normal auth success rate."""
        pass
```

---

#### **TrafficSpikeScenario**
**File:** `scenarios/scenario_traffic_spike.py`

**Responsibility:** Sudden traffic increase

**Pseudo-interface:**
```python
class TrafficSpikeScenario(BaseScenario):
    """
    Sudden increase in request volume.
    
    Affected Services:
    - APIService (primary)
    - DatabaseService (primary - connection pool)
    - All services (secondary - cascading impact)
    
    Intensity Effects:
    - LOW: 3x request volume, response time +200ms
    - MEDIUM: 10x request volume, response time +1000ms, rate limiting engaged
    - HIGH: 50x request volume, cascading failures, errors increase to 10-20%
    
    Logs Generated:
    - WARNING: Rate limit triggered, queue backlog
    - ERROR: 429 Too Many Requests, service overload
    """
    
    def get_affected_services(self) -> list[ServiceType]:
        """APIService, DatabaseService, and cascades to all."""
        pass
    
    def activate(self, service_manager, global_state) -> None:
        """Multiply request volume and add latency."""
        pass
    
    def deactivate(self, service_manager, global_state) -> None:
        """Return to normal traffic levels."""
        pass
```

---

#### **SystemDegradationScenario**
**File:** `scenarios/scenario_degradation.py`

**Responsibility:** Gradual resource exhaustion

**Pseudo-interface:**
```python
class SystemDegradationScenario(BaseScenario):
    """
    Gradual system resource exhaustion (memory leak, CPU creep).
    
    Affected Services:
    - All services (universal impact)
    
    Intensity Effects:
    - LOW: Memory +5%, CPU +5% per step, degradation over 10 minutes
    - MEDIUM: Memory +10%, CPU +10% per step, degradation over 5 minutes
    - HIGH: Memory +20%, CPU +20% per step, degradation over 2 minutes
    
    Logs Generated:
    - WARNING: High memory usage, high CPU usage
    - ERROR: Out of memory exception, process restart
    """
    
    def get_affected_services(self) -> list[ServiceType]:
        """All services."""
        pass
    
    def activate(self, service_manager, global_state) -> None:
        """Start gradual resource degradation."""
        pass
    
    def deactivate(self, service_manager, global_state) -> None:
        """Reset resource utilization."""
        pass
```

---

#### **ScenarioManager**
**File:** `scenarios/scenario_manager.py`

**Responsibility:** Manage scenario scheduling and transitions

**Pseudo-interface:**
```python
class ScenarioManager:
    """
    Manages scenario scheduling and transitions.
    
    Responsibilities:
    - Track active scenario
    - Schedule scenario changes
    - Smooth transitions between scenarios
    - Log scenario events
    """
    
    def __init__(self, service_manager: ServiceManager, global_state: GlobalState) -> None:
        """Initialize with dependencies."""
        pass
    
    def register_scenario(self, scenario: BaseScenario) -> None:
        """Register available scenario."""
        pass
    
    def set_active_scenario(self, scenario_type: ScenarioType, intensity: IntensityLevel, 
                           duration_seconds: int = None) -> None:
        """
        Transition to new scenario.
        
        If duration is set, auto-revert to NORMAL after duration.
        """
        pass
    
    def get_current_scenario(self) -> BaseScenario:
        """Get active scenario."""
        pass
    
    def get_scenario_by_type(self, scenario_type: ScenarioType) -> BaseScenario:
        """Retrieve scenario definition."""
        pass
    
    def update(self) -> None:
        """Check if scenario duration expired, revert if needed."""
        pass
    
    def get_all_scenarios(self) -> dict[ScenarioType, BaseScenario]:
        """List all available scenarios."""
        pass
```

---

### 2.4 Controller Layer

#### **SystemController**
**File:** `controller/system_controller.py`

**Responsibility:** Central orchestration of scenario transitions and state management

**Pseudo-interface:**
```python
class SystemController:
    """
    Central controller for system state and scenario transitions.
    
    Responsibilities:
    - Manage global system state
    - Coordinate scenario transitions
    - Schedule scenario changes over simulation
    - Ensure consistent state updates
    """
    
    def __init__(self, service_manager: ServiceManager, 
                 scenario_manager: ScenarioManager,
                 global_state: GlobalState) -> None:
        """Initialize controller with managers."""
        pass
    
    def initialize(self) -> None:
        """Setup initial state (NORMAL scenario)."""
        pass
    
    def transition_to_scenario(self, scenario: ScenarioType, intensity: IntensityLevel,
                              duration_seconds: int = None) -> None:
        """
        Transition to new scenario.
        
        Orchestrates:
        1. Deactivate current scenario
        2. Activate new scenario
        3. Update global state
        4. Notify all observers
        """
        pass
    
    def schedule_scenario_change(self, time_offset_seconds: int,
                                scenario: ScenarioType,
                                intensity: IntensityLevel) -> None:
        """Schedule scenario change at future time."""
        pass
    
    def update(self) -> None:
        """
        Called each simulation step.
        
        Responsibilities:
        - Check scheduled transitions
        - Update scenario managers
        - Update global state
        """
        pass
    
    def get_current_state_snapshot(self) -> SystemStateSnapshot:
        """Get complete current system state for export."""
        pass
```

---

### 2.5 Logging Layer

#### **LogEntry (Data Class)**
**File:** `logging/log_models.py`

**Responsibility:** Standardized log data structure

**Pseudo-interface:**
```python
@dataclass
class LogEntry:
    """
    Standardized log entry.
    
    Fields:
    - timestamp: When log occurred
    - service: Which service generated log
    - severity: Log level (INFO, WARNING, ERROR)
    - message: Log message
    - request_id: Trace ID for request correlation
    - duration_ms: Execution time
    - metadata: Additional context (error codes, user IDs, etc.)
    - scenario: Active scenario when log was generated
    - scenario_intensity: Scenario intensity level
    """
    
    timestamp: datetime
    service: str
    severity: Severity
    message: str
    request_id: str
    duration_ms: float
    metadata: dict
    scenario: ScenarioType
    scenario_intensity: IntensityLevel
```

---

#### **LoggingManager**
**File:** `logging/log_manager.py`

**Responsibility:** Centralized log collection and management

**Pseudo-interface:**
```python
class LoggingManager:
    """
    Manages log collection and output.
    
    Responsibilities:
    - Accept logs from services
    - Add metadata (timestamp, scenario, severity)
    - Route to console and file output
    - Track log statistics
    """
    
    def __init__(self, config: LoggingConfig, global_state: GlobalState) -> None:
        """Initialize with config and global state reference."""
        pass
    
    def log(self, service: str, severity: Severity, message: str,
            metadata: dict = None, duration_ms: float = 0) -> None:
        """
        Log event from service.
        
        Automatically adds:
        - Current timestamp
        - Current scenario info
        - Request ID (if in context)
        """
        pass
    
    def log_entry(self, entry: LogEntry) -> None:
        """Log pre-constructed entry."""
        pass
    
    def get_logs(self, filters: LogFilter = None) -> list[LogEntry]:
        """
        Retrieve logs with optional filtering.
        
        Filters can be:
        - Service name
        - Severity level
        - Time range
        - Scenario type
        """
        pass
    
    def export_logs(self, filepath: str, format: str = "jsonl") -> None:
        """Export all logs to file (JSONL format)."""
        pass
    
    def clear_logs(self) -> None:
        """Clear in-memory logs."""
        pass
    
    def get_statistics(self) -> LogStatistics:
        """Get aggregate log statistics."""
        pass
```

---

#### **LogFormatter**
**File:** `logging/log_formatter.py`

**Responsibility:** Format logs for output

**Pseudo-interface:**
```python
class LogFormatter:
    """
    Formats LogEntry objects for different output formats.
    
    Responsibilities:
    - Convert to JSONL format
    - Convert to human-readable format
    - Ensure consistency
    """
    
    def format_to_jsonl(self, entry: LogEntry) -> str:
        """
        Format as JSON Lines (one JSON per line).
        
        Output structure:
        {
            "timestamp": "2026-04-25T10:30:45.123Z",
            "service": "auth_service",
            "severity": "ERROR",
            "message": "...",
            "request_id": "req-12345",
            "duration_ms": 245.5,
            "metadata": {...},
            "scenario": "AUTH_FAILURE",
            "scenario_intensity": "HIGH"
        }
        """
        pass
    
    def format_to_human_readable(self, entry: LogEntry) -> str:
        """Format for console output."""
        pass
    
    def format_batch_to_jsonl(self, entries: list[LogEntry]) -> str:
        """Format multiple entries to JSONL."""
        pass
```

---

#### **LogWriter**
**File:** `logging/log_writer.py`

**Responsibility:** Write logs to output destinations

**Pseudo-interface:**
```python
class LogWriter:
    """
    Writes logs to console and file.
    
    Responsibilities:
    - Write to stdout
    - Write to JSONL file
    - Handle file rotation if needed
    """
    
    def __init__(self, output_dir: str, console_output: bool = True) -> None:
        """Initialize writer."""
        pass
    
    def write_to_console(self, formatted_log: str) -> None:
        """Write to stdout."""
        pass
    
    def write_to_file(self, formatted_log: str) -> None:
        """Append to JSONL file."""
        pass
    
    def flush(self) -> None:
        """Ensure all buffered data is written."""
        pass
    
    def close(self) -> None:
        """Close file handles."""
        pass
```

---

### 2.6 Utility Layer

#### **Constants & Enums**
**File:** `utils/constants.py`

**Responsibility:** Define project constants and enumerations

**Pseudo-interface:**
```python
class Severity(Enum):
    """Log severity levels."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class ScenarioType(Enum):
    """Scenario types."""
    NORMAL = "NORMAL"
    DB_LATENCY = "DB_LATENCY"
    AUTH_FAILURE = "AUTH_FAILURE"
    TRAFFIC_SPIKE = "TRAFFIC_SPIKE"
    SYSTEM_DEGRADATION = "SYSTEM_DEGRADATION"

class IntensityLevel(Enum):
    """Scenario intensity."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"

class ServiceType(Enum):
    """Microservice types."""
    AUTH = "AUTH_SERVICE"
    DATABASE = "DATABASE_SERVICE"
    API = "API_SERVICE"
```

---

#### **MetricsCollector**
**File:** `utils/metrics.py`

**Responsibility:** Track performance metrics during simulation

**Pseudo-interface:**
```python
class MetricsCollector:
    """
    Collects simulation metrics.
    
    Responsibilities:
    - Track request counts
    - Track error rates
    - Track response times
    - Track resource usage
    """
    
    def __init__(self) -> None:
        """Initialize metrics."""
        pass
    
    def record_request(self, service: str, response_time_ms: float, 
                      success: bool) -> None:
        """Record request execution."""
        pass
    
    def record_error(self, service: str, error_type: str) -> None:
        """Record error occurrence."""
        pass
    
    def set_resource_usage(self, cpu: float, memory: float, disk: float) -> None:
        """Record resource usage."""
        pass
    
    def get_metrics_summary(self) -> MetricsSummary:
        """Get aggregate metrics."""
        pass
    
    def export_metrics(self, filepath: str) -> None:
        """Export metrics to file."""
        pass
```

---

#### **InputValidator**
**File:** `utils/validators.py`

**Responsibility:** Validate configuration inputs

**Pseudo-interface:**
```python
class InputValidator:
    """
    Validates simulation configuration.
    
    Responsibilities:
    - Validate config values
    - Ensure consistency
    - Provide helpful error messages
    """
    
    @staticmethod
    def validate_scenario_config(config: dict) -> tuple[bool, str]:
        """Validate scenario definition."""
        pass
    
    @staticmethod
    def validate_service_config(config: dict) -> tuple[bool, str]:
        """Validate service configuration."""
        pass
    
    @staticmethod
    def validate_simulation_duration(duration: int) -> tuple[bool, str]:
        """Validate duration is positive."""
        pass
```

---

## 3. Data Flow

### 3.1 Simulation Initialization Flow

```
simulation_runner.py
    ↓
SimulationEngine.initialize_system()
    ├─→ ServiceManager.create_services()
    │   ├─→ AuthService.__init__()
    │   ├─→ DatabaseService.__init__()
    │   └─→ APIService.__init__()
    │
    ├─→ ServiceManager.initialize_all()
    │   ├─→ AuthService.initialize()
    │   ├─→ DatabaseService.initialize()
    │   └─→ APIService.initialize()
    │
    ├─→ ScenarioManager.register_scenario()
    │   ├─→ Register NormalScenario
    │   ├─→ Register DatabaseLatencyScenario
    │   ├─→ Register AuthFailureScenario
    │   ├─→ Register TrafficSpikeScenario
    │   └─→ Register SystemDegradationScenario
    │
    ├─→ SystemController.initialize()
    │   └─→ ScenarioManager.set_active_scenario(NORMAL)
    │
    └─→ LoggingManager initialized with output directory
```

---

### 3.2 Main Simulation Loop

```
SimulationEngine.run(duration_seconds)
    │
    ├─→ FOR each simulation_step (deterministic intervals):
    │   │
    │   ├─→ SimulationClock.advance()
    │   │   └─→ Updates current_time
    │   │
    │   ├─→ SystemController.update()
    │   │   ├─→ Check scheduled scenario transitions
    │   │   └─→ ScenarioManager.update()
    │   │       └─→ Update current scenario effects
    │   │
    │   ├─→ Generate requests (APIService)
    │   │   │
    │   │   └─→ APIService.process_request()
    │   │       ├─→ LoggingManager.log("API request received")
    │   │       ├─→ Call DatabaseService.process_request()
    │   │       │   ├─→ LoggingManager.log("Query executing")
    │   │       │   ├─→ Simulate query with latency
    │   │       │   └─→ LoggingManager.log("Query result" or "Query timeout")
    │   │       ├─→ Call AuthService.process_request() if needed
    │   │       │   ├─→ LoggingManager.log("Auth check")
    │   │       │   └─→ LoggingManager.log("Auth result")
    │   │       └─→ LoggingManager.log("API response sent")
    │   │
    │   └─→ Update GlobalState
    │       ├─→ Update service health metrics
    │       └─→ Update resource utilization
    │
    └─→ SimulationEngine.shutdown()
        ├─→ ServiceManager.shutdown_all()
        ├─→ LoggingManager.export_logs()
        └─→ MetricsCollector.export_metrics()
```

---

### 3.3 Scenario Effect Flow

```
SystemController.transition_to_scenario(TRAFFIC_SPIKE, HIGH)
    │
    ├─→ ScenarioManager.set_active_scenario()
    │   │
    │   ├─→ Current scenario.deactivate()
    │   │   └─→ Reset all services to normal
    │   │
    │   └─→ New scenario.activate()
    │       └─→ TrafficSpikeScenario.activate()
    │           ├─→ APIService.apply_scenario_effect()
    │           │   └─→ Set request_volume_multiplier = 50
    │           │   └─→ Increase response latency
    │           │
    │           ├─→ DatabaseService.apply_scenario_effect()
    │           │   └─→ Connection pool under stress
    │           │
    │           └─→ GlobalState.set_current_scenario(TRAFFIC_SPIKE, HIGH)
    │
    └─→ Subsequent service requests now see amplified effects
        ├─→ APIService.process_request()
        │   └─→ Generates 50x normal load
        │       └─→ LoggingManager logs "Rate limit triggered"
        │       └─→ LoggingManager logs "429 Too Many Requests"
        │
        └─→ DatabaseService logs connection pool exhaustion
```

---

### 3.4 Request Processing Flow (High Detail)

```
APIService.process_request(HTTPRequest)
    │
    ├─→ LoggingManager.log("INFO", "Request received", 
    │                      metadata={"method": "GET", "path": "/api/users"})
    │
    ├─→ Check AuthService if needed
    │   │
    │   └─→ AuthService.process_request(AuthRequest)
    │       ├─→ Check auth token
    │       ├─→ If TRAFFIC_SPIKE scenario active:
    │       │   └─→ Apply additional latency
    │       ├─→ If AUTH_FAILURE scenario active:
    │       │   └─→ Random rejection based on intensity
    │       │
    │       └─→ LoggingManager.log results
    │           ├─→ If success: "INFO", "User authenticated"
    │           └─→ If failure: "ERROR", "Auth failed"
    │
    ├─→ Call DatabaseService for data
    │   │
    │   └─→ DatabaseService.process_request(DatabaseQuery)
    │       ├─→ Acquire connection from pool
    │       ├─→ If DB_LATENCY scenario active:
    │       │   └─→ Add latency based on intensity
    │       ├─→ If TRAFFIC_SPIKE scenario active:
    │       │   └─→ Pool may be exhausted → timeout
    │       │
    │       └─→ LoggingManager.log results
    │           ├─→ If success: "INFO", "Query completed in 120ms"
    │           └─→ If timeout: "ERROR", "Query timeout after 30s"
    │
    ├─→ Aggregate response
    │
    ├─→ LoggingManager.log("INFO", "Response sent", 
    │                      metadata={"status": 200, "response_time_ms": 245})
    │
    └─→ Return HTTPResponse
```

---

### 3.5 Log Generation During Degradation Scenario

```
SystemController.transition_to_scenario(SYSTEM_DEGRADATION, HIGH)
    │
    ├─→ GlobalState.set_resource_metrics(cpu=30%, memory=50%)
    │
    └─→ Each simulation step:
        │
        ├─→ SystemDegradationScenario.activate() effects accumulate
        │   ├─→ CPU += 20% per step → 50%, 70%, 90%, OOM
        │   └─→ Memory += 20% per step
        │
        ├─→ Services notice high resource usage
        │   │
        │   ├─→ DatabaseService
        │   │   └─→ LoggingManager.log("WARNING", "High memory usage", 
        │   │       metadata={"memory_percent": 70})
        │   │
        │   ├─→ APIService
        │   │   └─→ LoggingManager.log("WARNING", "High CPU usage",
        │   │       metadata={"cpu_percent": 85})
        │   │
        │   └─→ All services start failing
        │       └─→ LoggingManager.log("ERROR", "Out of memory exception")
        │
        └─→ Result: Increasingly dense ERROR logs over time
```

---

### 3.6 Log Export Structure

```
Logs are collected in memory during simulation, then exported as JSONL:

logs_2026_04_25_simrun_001.jsonl:

{"timestamp":"2026-04-25T10:00:00.000Z","service":"api_service","severity":"INFO","message":"API server started","request_id":null,"duration_ms":0,"metadata":{"port":8080},"scenario":"NORMAL","scenario_intensity":"MEDIUM"}
{"timestamp":"2026-04-25T10:00:01.500Z","service":"api_service","severity":"INFO","message":"Request received","request_id":"req-001","duration_ms":0,"metadata":{"method":"GET","path":"/api/users"},"scenario":"NORMAL","scenario_intensity":"MEDIUM"}
{"timestamp":"2026-04-25T10:00:01.520Z","service":"auth_service","severity":"INFO","message":"User authenticated","request_id":"req-001","duration_ms":20,"metadata":{"user_id":"123"},"scenario":"NORMAL","scenario_intensity":"MEDIUM"}
{"timestamp":"2026-04-25T10:00:01.650Z","service":"database_service","severity":"INFO","message":"Query completed","request_id":"req-001","duration_ms":130,"metadata":{"rows_returned":50,"query_time_ms":127},"scenario":"NORMAL","scenario_intensity":"MEDIUM"}
{"timestamp":"2026-04-25T10:00:01.780Z","service":"api_service","severity":"INFO","message":"Response sent","request_id":"req-001","duration_ms":280,"metadata":{"status":200,"response_size_bytes":5240},"scenario":"NORMAL","scenario_intensity":"MEDIUM"}

... (thousands more entries) ...

{"timestamp":"2026-04-25T10:05:30.000Z","service":"system_controller","severity":"INFO","message":"Scenario transition","request_id":null,"duration_ms":0,"metadata":{"from_scenario":"NORMAL","to_scenario":"TRAFFIC_SPIKE","intensity":"HIGH"},"scenario":"TRAFFIC_SPIKE","scenario_intensity":"HIGH"}
{"timestamp":"2026-04-25T10:05:31.200Z","service":"api_service","severity":"WARNING","message":"Rate limit triggered","request_id":"req-1250","duration_ms":0,"metadata":{"requests_per_second":500},"scenario":"TRAFFIC_SPIKE","scenario_intensity":"HIGH"}
{"timestamp":"2026-04-25T10:05:31.350Z","service":"database_service","severity":"ERROR","message":"Connection pool exhausted","request_id":"req-1251","duration_ms":30000,"metadata":{"pool_size":100,"active_connections":102},"scenario":"TRAFFIC_SPIKE","scenario_intensity":"HIGH"}
```

---

## 4. Key Design Patterns

### 4.1 Observer Pattern
- `GlobalState` maintains observers (services) that react to state changes
- Services subscribe to scenario transitions

### 4.2 Factory Pattern
- `ServiceManager` creates all service instances
- `ScenarioManager` instantiates scenarios on demand

### 4.3 Strategy Pattern
- Each `BaseScenario` implements different effects strategy
- Each service applies scenario effects differently

### 4.4 Dependency Injection
- `LoggingManager` injected into all services
- `GlobalState` passed to controller and scenarios
- `ServiceManager` and `ScenarioManager` managed by controller

### 4.5 Deterministic Design
- `SimulationClock` provides consistent time across all components
- Seeding enables reproducible simulations
- No random time-based events—only controlled scenario transitions

---

## 5. Configuration Structure

```python
# config.py structure

SimulationConfig:
    duration_seconds: int
    clock_seed: int (for reproducibility)
    clock_speed_multiplier: float
    
ServiceConfig:
    enabled_services: List[ServiceType]
    auth_service_config: {...}
    database_service_config: {...}
    api_service_config: {...}
    
ScenarioConfig:
    scenario_schedule: List[ScenarioSchedule]
        - time_offset_seconds: int
        - scenario_type: ScenarioType
        - intensity: IntensityLevel
        - duration_seconds: int (optional)
    
LoggingConfig:
    output_directory: str
    export_format: str ("jsonl")
    console_output: bool
    
RequestGenerationConfig:
    requests_per_second: int
    request_distribution: str ("uniform", "poisson", "bursty")
```

---

## 6. Reproducibility & Determinism

**Key Principles:**
1. `SimulationClock` with fixed seed ensures time progression is identical
2. All random events use seeded RNG (not system RNG)
3. Scenario transitions scheduled deterministically by time, not events
4. Request generation follows deterministic distribution
5. Service behavior based on scenario state, not random chance

**Result:** Run simulation twice with same config + seed = identical logs

---

## 7. Extensibility Points

### Adding New Services:
1. Create `services/new_service.py`
2. Inherit from `BaseService`
3. Implement required methods
4. Register in `ServiceManager.create_services()`

### Adding New Scenarios:
1. Create `scenarios/scenario_new_anomaly.py`
2. Inherit from `BaseScenario`
3. Implement `activate()` and `deactivate()`
4. Register in `ScenarioManager.__init__()`

### Custom Log Processing:
1. Extend `LogFormatter` for new output formats
2. Extend `LogWriter` for new output destinations
3. Add filters in `LoggingManager.get_logs()`

---

## Summary

This architecture provides:
- **Modularity**: Each component has single responsibility
- **Testability**: Services isolated, can be tested independently
- **Realism**: Simulates realistic microservice interactions
- **Reproducibility**: Deterministic execution for ML training
- **Extensibility**: Easy to add new services/scenarios
- **Traceability**: Rich logging with metadata for anomaly detection

Perfect foundation for generating high-quality training data for AI anomaly detection models.
