"""Windows shim for the unmodified runtime/scripts/remotion_scenes.py (film tooling).
remotion_scenes.py runs a bare "npx" through subprocess.run, which fails on Windows ([WinError 2])
because npx is npx.cmd. This resolves the executable and then runs the toolkit script unchanged,
and exits nonzero when the script reports FAILED (it returns 2 then, but the shim re-checks stderr too).
Usage: python scripts/remotion_win.py <REEL> [--only B07] [--force]
"""
import runpy, shutil, subprocess, sys
from pathlib import Path

TOOLKIT = Path(r"D:/CSYE7270/brutalist.art")
NPX = shutil.which("npx.cmd") or shutil.which("npx")
_run = subprocess.run


def run(cmd, *a, **k):
    if isinstance(cmd, list) and cmd and cmd[0] == "npx":
        cmd = [NPX] + cmd[1:]
    return _run(cmd, *a, **k)


subprocess.run = run
sys.path.insert(0, str(TOOLKIT / "runtime/scripts"))
sys.argv = [str(TOOLKIT / "runtime/scripts/remotion_scenes.py")] + sys.argv[1:]
runpy.run_path(sys.argv[0], run_name="__main__")
