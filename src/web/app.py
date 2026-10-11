import os
import re
import time
import asyncio
import logging
from pathlib import Path
from typing import List, Optional

from fastapi import FastAPI, UploadFile, File, Request, Response, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from src.web.cluster_manager import ClusterManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("entropy_streamer")

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent
VIDEOS_DIR = BASE_DIR / "data" / "videos"
STATIC_DIR = BASE_DIR / "src" / "web" / "static"

VIDEOS_DIR.mkdir(parents=True, exist_ok=True)
STATIC_DIR.mkdir(parents=True, exist_ok=True)

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing Entropy Cluster Streaming Engine...")
    task = asyncio.create_task(background_telemetry_loop())
    yield
    task.cancel()

app = FastAPI(title="Entropy-Guided Cluster Video Streamer", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Cluster Manager
cluster_mgr = ClusterManager(num_nodes=16, nodes_per_rack=4)

# Active WebSocket connections
connected_websockets: List[WebSocket] = []

async def background_telemetry_loop():
    """
    Periodically decays node loads and broadcasts cluster state to WebSocket clients.
    """
    while True:
        try:
            cluster_mgr.tick_decay()
            if connected_websockets:
                state = cluster_mgr.get_cluster_state()
                dead_sockets = []
                for ws in connected_websockets:
                    try:
                        await ws.send_json({"type": "TELEMETRY", "data": state})
                    except Exception:
                        dead_sockets.append(ws)
                for ws in dead_sockets:
                    if ws in connected_websockets:
                        connected_websockets.remove(ws)
        except Exception as e:
            logger.error(f"Error in telemetry loop: {e}")
        await asyncio.sleep(0.4)

# Mount Static Files
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

@app.get("/", response_class=HTMLResponse)
async def serve_index():
    index_file = STATIC_DIR / "index.html"
    if not index_file.exists():
        return HTMLResponse("<h2>Frontend building in progress...</h2>")
    with open(index_file, "r", encoding="utf-8") as f:
        return HTMLResponse(
            f.read(),
            headers={"Cache-Control": "no-cache, no-store, must-revalidate"}
        )

@app.get("/api/videos")
async def list_videos():
    """
    Lists all available video files in the repository.
    """
    video_extensions = {".mp4", ".webm", ".mkv", ".mov"}
    files = []
    for f in VIDEOS_DIR.iterdir():
        if f.is_file() and f.suffix.lower() in video_extensions:
            stat = f.stat()
            files.append({
                "filename": f.name,
                "size_bytes": stat.st_size,
                "size_mb": round(stat.st_size / (1024 * 1024), 2),
                "modified": stat.st_mtime
            })
    files.sort(key=lambda x: x["filename"] != "demo_stream.mp4")
    return {"videos": files}

@app.post("/api/upload")
async def upload_video(file: UploadFile = File(...)):
    """
    Uploads a video to the cluster video repository and triggers ingestion load.
    """
    # Sanitize filename
    clean_name = re.sub(r'[^a-zA-Z0-9_\-\.]', '_', file.filename)
    target_path = VIDEOS_DIR / clean_name
    
    # Save file in chunks
    chunk_size = 1024 * 1024 # 1MB chunks
    bytes_written = 0
    with open(target_path, "wb") as out_file:
        while content := await file.read(chunk_size):
            out_file.write(content)
            bytes_written += len(content)
            # Dispatch ingestion job to cluster for each uploaded MB
            cluster_mgr.dispatch_chunk(clean_name, chunk_index=bytes_written // chunk_size, byte_size=len(content))

    return {
        "status": "success",
        "filename": clean_name,
        "size_bytes": bytes_written,
        "size_mb": round(bytes_written / (1024 * 1024), 2),
        "message": f"Successfully ingested {clean_name} into cluster storage"
    }

@app.get("/api/stream/{filename}")
async def stream_video(filename: str, request: Request):
    """
    HTTP 206 Partial Content Video Streaming with chunk-level load balancer dispatch.
    As the video player requests byte ranges, each range triggers a load balancing decision.
    """
    file_path = VIDEOS_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Video not found")

    file_size = file_path.stat().st_size
    range_header = request.headers.get("Range")

    if range_header:
        # Standard HTTP Range parsing (RFC 7233)
        start = 0
        end = file_size - 1

        match = re.match(r"bytes=(\d*)-(\d*)", range_header.strip())
        if match:
            s_str, e_str = match.groups()
            if s_str and e_str:
                start = int(s_str)
                end = int(e_str)
            elif s_str:
                start = int(s_str)
                end = file_size - 1
            elif e_str:
                # Suffix byte range
                suffix = int(e_str)
                start = max(0, file_size - suffix)
                end = file_size - 1

        # If start is beyond file_size in simulated streaming, cycle through file
        if start >= file_size and file_size > 0:
            eff_start = start % file_size
            eff_end = min(eff_start + (end - start), file_size - 1)
        elif start < 0 or end < start:
            return Response(
                status_code=416,
                headers={"Content-Range": f"bytes */{file_size}"}
            )
        else:
            eff_start = start
            eff_end = min(end, file_size - 1)

        chunk_length = max(0, eff_end - eff_start + 1)
        chunk_index = start // (512 * 1024)

        if chunk_length > 0:
            # Dispatch chunk to load balancer (Algorithm 2)
            event = cluster_mgr.dispatch_chunk(filename, chunk_index=chunk_index, byte_size=chunk_length)

            # Broadcast immediate dispatch event
            if connected_websockets:
                for ws in connected_websockets:
                    try:
                        asyncio.create_task(ws.send_json({"type": "CHUNK_DISPATCHED", "event": event}))
                    except Exception:
                        pass

        with open(file_path, "rb") as f:
            f.seek(eff_start)
            data = f.read(chunk_length) if chunk_length > 0 else b""

        headers = {
            "Content-Range": f"bytes {start}-{end if start < file_size else start + len(data) - 1}/{file_size if start < file_size else '*'}",
            "Accept-Ranges": "bytes",
            "Content-Length": str(len(data)),
            "Content-Type": "video/mp4",
        }
        return Response(content=data, status_code=206, headers=headers, media_type="video/mp4")
    else:
        # Full content
        event = cluster_mgr.dispatch_chunk(filename, chunk_index=0, byte_size=file_size)
        if connected_websockets:
            for ws in connected_websockets:
                try:
                    asyncio.create_task(ws.send_json({"type": "CHUNK_DISPATCHED", "event": event}))
                except Exception:
                    pass
        return FileResponse(file_path, media_type="video/mp4")

@app.post("/api/stream/dispatch_chunk")
async def dispatch_stream_chunk(request: Request):
    """
    Live stream chunk dispatcher: Simulates or triggers active chunk dispatch during playback.
    Executes Algorithm 2, broadcasts to connected WebSockets, and returns the decision event.
    """
    try:
        body = await request.json()
    except Exception:
        body = {}
    video_name = body.get("video_name", "demo_stream.mp4")
    chunk_index = int(body.get("chunk_index", 0))
    byte_size = int(body.get("byte_size", 256 * 1024))

    event = cluster_mgr.dispatch_chunk(video_name, chunk_index=chunk_index, byte_size=byte_size)

    if connected_websockets:
        for ws in connected_websockets:
            try:
                asyncio.create_task(ws.send_json({"type": "CHUNK_DISPATCHED", "event": event}))
            except Exception:
                pass

    return {"status": "dispatched", "event": event}

@app.post("/api/action/burst")
async def trigger_burst(request: Request):
    """
    Simulates a hotspot spike on a rack to demonstrate entropy stability classification
    and the tree steering traffic away from volatile/loaded racks.
    """
    body = await request.json() if request.headers.get("content-type") == "application/json" else {}
    rack_id = body.get("rack_id", None)
    magnitude = float(body.get("magnitude", 65.0))
    result = cluster_mgr.inject_burst(rack_id=rack_id, magnitude=magnitude)
    return {"status": "burst_injected", "details": result}

@app.post("/api/action/rebalance")
async def trigger_rebalance():
    """
    Invokes Algorithm 3: Dynamic Entropy Rebalancing.
    """
    result = cluster_mgr.trigger_rebalance()
    return {"status": "rebalance_complete", "details": result}

@app.get("/api/cluster/state")
async def get_cluster_state():
    return cluster_mgr.get_cluster_state()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_websockets.append(websocket)
    try:
        # Send initial cluster snapshot
        await websocket.send_json({"type": "TELEMETRY", "data": cluster_mgr.get_cluster_state()})
        while True:
            # Handle inbound commands if any
            msg = await websocket.receive_json()
            action = msg.get("action")
            if action == "burst":
                res = cluster_mgr.inject_burst()
                await websocket.send_json({"type": "BURST_RESULT", "data": res})
            elif action == "rebalance":
                res = cluster_mgr.trigger_rebalance()
                await websocket.send_json({"type": "REBALANCE_RESULT", "data": res})
    except WebSocketDisconnect:
        if websocket in connected_websockets:
            connected_websockets.remove(websocket)
    except Exception as e:
        logger.warning(f"WebSocket client error: {e}")
        if websocket in connected_websockets:
            connected_websockets.remove(websocket)
