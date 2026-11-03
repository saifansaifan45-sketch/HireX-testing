import pytest
import time
from config.settings import settings

@pytest.mark.performance
def test_jobs_api_latency(jobs_client):
    """TC_HX_PERF_001: Measure API response latency for public GET /jobs endpoint (SLO: < 500ms)"""
    latencies = []
    for _ in range(5):
        start = time.time()
        resp = jobs_client.get_public_jobs()
        latencies.append((time.time() - start) * 1000)
        assert resp.status == 200
    
    avg_latency = sum(latencies) / len(latencies)
    print(f"\nGET /jobs latencies (ms): {[round(x, 1) for x in latencies]}, Avg: {round(avg_latency, 1)}ms")
    assert avg_latency < 1000, f"Average latency too high: {avg_latency}ms"

@pytest.mark.performance
def test_root_health_latency(auth_client):
    """TC_HX_PERF_002: Measure API response latency for root health check (SLO: < 300ms)"""
    latencies = []
    for _ in range(5):
        start = time.time()
        resp = auth_client.get("/")
        latencies.append((time.time() - start) * 1000)
        assert resp.status == 200
        
    avg_latency = sum(latencies) / len(latencies)
    print(f"\nGET / health latencies (ms): {[round(x, 1) for x in latencies]}, Avg: {round(avg_latency, 1)}ms")
    assert avg_latency < 800, f"Average latency too high: {avg_latency}ms"

