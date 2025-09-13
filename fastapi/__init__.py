import os

# Location of this shim package
_shim_path = os.path.dirname(__file__)

# Execute the original FastAPI package in this module's namespace so that
# we effectively act as a transparent proxy.  This allows us to provide a
# lightweight ``fastapi.testclient`` without requiring the optional ``httpx``
# dependency used by the upstream test client.

_real_fastapi_path = "/root/.pyenv/versions/3.12.10/lib/python3.12/site-packages/fastapi"
__file__ = os.path.join(_real_fastapi_path, "__init__.py")
# Ensure our shim path comes first so that ``fastapi.testclient`` resolves here
__path__ = [_shim_path, _real_fastapi_path]

with open(__file__, "r") as f:
    code = compile(f.read(), __file__, "exec")
    exec(code, globals())

# Import the local lightweight test client implementation
from .testclient import TestClient  # noqa: E402
