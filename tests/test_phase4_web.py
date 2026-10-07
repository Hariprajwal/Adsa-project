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

if __name__ == "__main__":
    test_web_routes()
    print("\nALL PHASE 4 TESTS PASSED!")
