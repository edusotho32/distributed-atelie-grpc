from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
PROTO_ROOT = ROOT / "proto"
PROTO_FILE = PROTO_ROOT / "atelie_grpc" / "atelie.proto"
OUTPUT = ROOT / "src"

subprocess.run(
    [
        sys.executable,
        "-m",
        "grpc_tools.protoc",
        f"-I{PROTO_ROOT}",
        f"--python_out={OUTPUT}",
        f"--grpc_python_out={OUTPUT}",
        str(PROTO_FILE),
    ],
    check=True,
)
print("Stubs gerados em src/atelie_grpc")
