import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient
from src.web.app import app

def test_web_routes():
    client = TestClient(app)
    
    # 1. Test Index
    res = client.get("/")
    assert res.status_code == 200
    assert "ENTROPY-STREAM" in res.text
    print("[OK] Index page loads successfully")

    # 2. Test Videos API
    res = client.get("/api/videos")
    assert res.status_code == 200
    videos = res.json().get("videos", [])
    assert len(videos) > 0
    assert any(v["filename"] == "demo_stream.mp4" for v in videos)
    print(f"[OK] Video list returned: {[v['filename'] for v in videos]}")

    # 3. Test Video Streaming with Range Header (Chunk-level dispatch)
    res = client.get("/api/stream/demo_stream.mp4", headers={"Range": "bytes=0-1023"})
    assert res.status_code == 206
    assert "bytes 0-1023" in res.headers.get("Content-Range", "")
    assert len(res.content) == 1024
    print("[OK] Partial video stream (206) with chunk dispatch verified")

    # 3b. Test Dedicated Live Dispatch Chunk Endpoint
    res = client.post("/api/stream/dispatch_chunk", json={"video_name": "demo_stream.mp4", "chunk_index": 1, "byte_size": 256000})
    assert res.status_code == 200
    dispatch_data = res.json()
    assert dispatch_data["status"] == "dispatched"
    assert "event" in dispatch_data
    assert "simulation" in dispatch_data["event"]
    assert "step1_rack" in dispatch_data["event"]["simulation"]
    print("[OK] Live stream chunk dispatch endpoint with simulation trace verified")

    # 4. Test Cluster State
    res = client.get("/api/cluster/state")
    assert res.status_code == 200
    data = res.json()
    assert "root" in data
    assert "racks" in data
    assert len(data["racks"]) == 4
    assert len(data["nodes"]) == 16
    print(f"[OK] Cluster topology verified: {len(data['nodes'])} nodes across {len(data['racks'])} racks")

    # 5. Test Burst Injection
    res = client.post("/api/action/burst", json={"rack_id": 2, "magnitude": 60.0})
    assert res.status_code == 200
    assert res.json()["details"]["target_rack"] == 2
    print("[OK] Burst traffic injection verified on Rack 2")

    # 6. Test Periodic Rebalancing
    res = client.post("/api/action/rebalance")
    assert res.status_code == 200
    assert "was_rebuilt" in res.json()["details"]
    print("[OK] Algorithm 3 dynamic rebalancing triggered successfully")

    # 7. Test Policy Comparison Table in Cluster State
    res = client.get("/api/cluster/state")
    assert res.status_code == 200
    state_data = res.json()
    assert "policy_comparison_table" in state_data
    table = state_data["policy_comparison_table"]
    assert len(table) == 6
    expected_policies = {"hierarchical", "round_robin", "least_loaded", "work_queue", "random", "work_stealing"}
    assert {row["key"] for row in table} == expected_policies
    for row in table:
        assert "name" in row
        assert "rule" in row
        assert "complexity" in row
        assert "avg_latency_us" in row
        assert "variance" in row
        assert "jain_fairness" in row
        assert "dispatches" in row
    print("[OK] Policy comparison table across all 6 baselines verified")

    # 8. Test Set Policy Endpoint
    for pol in ["round_robin", "work_stealing", "hierarchical"]:
        res = client.post("/api/action/set_policy", json={"policy": pol})
        assert res.status_code == 200
        assert res.json()["active_algorithm"] == pol
    print("[OK] Set policy endpoint successfully switched modes")

    # 9. Test Pure Mode Traffic Simulation
    res = client.post("/api/action/simulate_traffic", json={"count": 5, "policy": "work_stealing"})
    assert res.status_code == 200
    sim_data = res.json()
    assert sim_data["status"] == "simulation_complete"
    assert sim_data["count"] == 5
    assert sim_data["active_policy"] == "work_stealing"
    assert sim_data["last_event"]["active_policy"] == "work_stealing"
    print("[OK] Pure mode traffic simulation verified")

if __name__ == "__main__":
    test_web_routes()
    print("\nALL PHASE 4 TESTS PASSED!")
