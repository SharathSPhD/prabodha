import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GUARD = ROOT / "scripts/lib/gpu_guard.sh"

def _run(env_extra="", args="smoke 3 L1"):
    cmd = f'source {GUARD} && gpu_guard_check {args}'
    return subprocess.run(["bash", "-c", cmd], capture_output=True, text=True,
                          env={"PATH": "/usr/bin:/bin", "PRABODHA_ROOT": str(ROOT),
                               **dict(kv.split("=", 1) for kv in env_extra.split() if kv)})

def test_simulate_mode_passes():
    r = _run("GUARD_SIMULATE=1")
    assert r.returncode == 0 and "ok" in r.stdout

def test_kill_switch_refuses(tmp_path):
    ks = ROOT / "research/KILL_SWITCH"
    ks.write_text("halt")
    try:
        r = _run("GUARD_SIMULATE=1")
        assert r.returncode != 0 and "kill switch" in r.stdout
    finally:
        ks.unlink()

def test_no_gpu_host_refuses_real(tmp_path):
    # Simulate a no-GPU host on ANY machine (incl. the Spark) by emptying PATH so
    # `command -v nvidia-smi` fails; the guard must refuse before touching pgrep.
    cmd = f'source {GUARD} && gpu_guard_check real 30 L1'
    r = subprocess.run(["/bin/bash", "-c", cmd], capture_output=True, text=True,
                       env={"PATH": str(tmp_path), "PRABODHA_ROOT": str(ROOT)})
    assert r.returncode != 0 and "no nvidia-smi" in r.stdout
