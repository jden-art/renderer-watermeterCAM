import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from fastapi import FastAPI, Header, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="ESP32-CAM Phase 1 Server")

# Directory setup
STORAGE_DIR = Path("./storage")
STORAGE_DIR.mkdir(exist_ok=True)
DB_DIR = Path("./data")
DB_DIR.mkdir(exist_ok=True)
DB_PATH = DB_DIR / "meter_data.db"

# Mount storage so you can view images via browser: /storage/2025/01/15/filename.jpg
app.mount("/storage", StaticFiles(directory="storage"), name="storage")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            filename TEXT NOT NULL,
            filepath TEXT NOT NULL,
            device_id TEXT,
            size_bytes INTEGER
        )
    """)
    conn.commit()
    conn.close()

init_db()

@app.get("/api/health")
def health():
    return {"status": "ok", "time": datetime.now(timezone.utc).isoformat()}

@app.post("/api/upload")
async def upload_image(
    request: Request,
    device_id: str = Header(default="esp32cam_01", alias="x-device-id")
):
    """
    Accepts raw JPEG bytes in the body.
    Headers:
        Content-Type: image/jpeg
        X-Device-ID: <your_device_name>
    """
    body = await request.body()
    if len(body) == 0:
        raise HTTPException(status_code=400, detail="Empty request body")

    now = datetime.now(timezone.utc)
    ts = now.strftime("%Y%m%d_%H%M%S_%f")[:-3]  # include milliseconds
    date_folder = now.strftime("%Y/%m/%d")
    folder = STORAGE_DIR / date_folder
    folder.mkdir(parents=True, exist_ok=True)

    filename = f"{device_id}_{ts}.jpg"
    filepath = folder / filename

    with open(filepath, "wb") as f:
        f.write(body)

    conn = get_db()
    c = conn.cursor()
    c.execute(
        "INSERT INTO images (timestamp, filename, filepath, device_id, size_bytes) VALUES (?, ?, ?, ?, ?)",
        (now.isoformat(), filename, str(filepath), device_id, len(body))
    )
    conn.commit()
    conn.close()

    return JSONResponse({
        "success": True,
        "filename": filename,
        "timestamp": now.isoformat(),
        "size_bytes": len(body)
    })

@app.get("/api/images/latest")
def latest_image():
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM images ORDER BY id DESC LIMIT 1")
    row = c.fetchone()
    conn.close()
    if not row:
        return {"message": "No images uploaded yet"}
    return dict(row)

@app.get("/api/images/count")
def image_count():
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) as c FROM images")
    row = c.fetchone()
    conn.close()
    return {"count": row["c"]}
