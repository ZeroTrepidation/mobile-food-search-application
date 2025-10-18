from __future__ import annotations

import json
import threading
from pathlib import Path
from typing import Optional

import uvicorn
from fastapi import FastAPI
from fastapi.responses import JSONResponse


class MockSodaServer:
    def __init__(self, fixtures_dir: Path, dataset_id: str):
        self.app = FastAPI()
        self._fixtures_dir = Path(fixtures_dir)
        self._dataset_id = dataset_id
        self._server: Optional[uvicorn.Server] = None
        self._thread: Optional[threading.Thread] = None

        @self.app.get("/resource/{dataset}.json")
        async def resource(dataset: str):
            # ignore dataset value; serve the fixture for simplicity
            data_path = self._fixtures_dir / "soda_providers.json"
            with data_path.open("r", encoding="utf-8") as f:
                data = json.load(f)
            return JSONResponse(content=data)

        @self.app.get("/api/views/{dataset}.json")
        async def views(dataset: str):
            meta_path = self._fixtures_dir / "soda_views.json"
            with meta_path.open("r", encoding="utf-8") as f:
                data = json.load(f)
            return JSONResponse(content=data)

    def start(self, host: str = "127.0.0.1", port: int = 0) -> int:
        config = uvicorn.Config(self.app, host=host, port=port, log_level="error")
        self._server = uvicorn.Server(config)

        def run():
            # run will block; serve in thread
            self._server.run()

        self._thread = threading.Thread(target=run, daemon=True)
        self._thread.start()
        # Wait until server has started and got the actual port
        # uvicorn doesn't expose a direct signal; poll until started
        import time
        for _ in range(50):
            if self._server.started and self._server.servers:
                # Retrieve the first server's socket address
                sock = next(iter(self._server.servers)).sockets[0]
                return sock.getsockname()[1]
            time.sleep(0.1)
        # Fallback to configured port (may be 0)
        return port

    def stop(self):
        if self._server and self._server.started:
            self._server.should_exit = True
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2)
