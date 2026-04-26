"""Basic tests for the log simulator"""

import pytest
from simulator import LogSimulator
from log_generator.constants import Scenario, Intensity


def test_log_simulator_initialization():
    """Test that LogSimulator initializes correctly"""
    sim = LogSimulator(seed=42)
    assert len(sim.logs) == 0
    assert sim.current_time is not None


def test_generate_normal_logs():
    """Test generating normal logs"""
    sim = LogSimulator(seed=42)
    sim.generate_logs(10, Scenario.NORMAL, Intensity.LOW)
    # Should generate approximately num_logs logs (distributed across services)
    assert len(sim.logs) > 0
    # Check that all logs have normal scenario
    for log in sim.logs:
        assert log.scenario == Scenario.NORMAL.value


def test_export_jsonl(tmp_path):
    """Test JSONL export"""
    sim = LogSimulator(seed=42)
    sim.generate_logs(5, Scenario.NORMAL, Intensity.LOW)
    
    output_file = tmp_path / "test_logs.jsonl"
    sim.export_jsonl(str(output_file))
    
    # Check file was created and has content
    assert output_file.exists()
    with open(output_file, 'r') as f:
        lines = f.readlines()
        assert len(lines) > 0  # Should have some logs
        # Check each line is valid JSON
        import json
        for line in lines:
            json.loads(line.strip())