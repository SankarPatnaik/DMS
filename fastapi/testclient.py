"""A very small TestClient for FastAPI used in the kata environment.

This implementation avoids the dependency on ``httpx`` that the official
FastAPI/Starlette TestClient requires.  It spins up an ASGI server in a
background thread using ``uvicorn`` and sends requests to it via the
``requests`` library.  Only the features exercised in the tests are
implemented: ``get`` and ``post`` requests with JSON or multipart data.
"""

from __future__ import annotations

import requests
import socket
import threading
import time
from typing import Any, Dict, Iterable, Tuple

import uvicorn


class TestClient:
    def __init__(self, app) -> None:
        self.app = app
        self._server: uvicorn.Server | None = None
        self._thread: threading.Thread | None = None
        self._port: int | None = None
        self._start_server()

    # ------------------------------------------------------------------
    # server management
    def _start_server(self) -> None:
        sock = socket.socket()
        sock.bind(("127.0.0.1", 0))
        _, port = sock.getsockname()
        sock.close()
        config = uvicorn.Config(self.app, host="127.0.0.1", port=port, log_level="error")
        server = uvicorn.Server(config=config)
        thread = threading.Thread(target=server.run, daemon=True)
        thread.start()
        # Wait for the server to start accepting connections
        while not server.started:
            time.sleep(0.01)
        self._server = server
        self._thread = thread
        self._port = port

    def _stop_server(self) -> None:
        if self._server is not None:
            self._server.should_exit = True
        if self._thread is not None:
            self._thread.join(timeout=1)

    def __enter__(self) -> "TestClient":  # pragma: no cover - not used in tests
        return self

    def __exit__(self, exc_type, exc, tb) -> None:  # pragma: no cover - not used in tests
        self.close()

    def close(self) -> None:
        self._stop_server()

    def __del__(self) -> None:  # pragma: no cover - cleanup on GC
        self.close()

    # ------------------------------------------------------------------
    # request helpers
    @property
    def base_url(self) -> str:
        assert self._port is not None
        return f"http://127.0.0.1:{self._port}"

    def request(self, method: str, url: str, **kwargs: Any) -> requests.Response:
        return requests.request(method, self.base_url + url, **kwargs)

    def get(self, url: str, params: Dict[str, Any] | None = None, **kwargs: Any) -> requests.Response:
        return self.request("GET", url, params=params, **kwargs)

    def post(
        self,
        url: str,
        data: Dict[str, Any] | None = None,
        files: Dict[str, Tuple[str, bytes, str]] | None = None,
        json: Any | None = None,
        **kwargs: Any,
    ) -> requests.Response:
        return self.request("POST", url, data=data, files=files, json=json, **kwargs)


__all__ = ["TestClient"]
