import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from atelie_grpc.client import run  # noqa: E402
from atelie_grpc.server import create_server  # noqa: E402


server, port = create_server(port=0)
server.start()
try:
    run(f"127.0.0.1:{port}")
finally:
    server.stop(grace=0).wait()
