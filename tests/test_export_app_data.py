"""Tests for export_app_data.py — gate + trace reader, data exporter.

Concept: niryātana (emission; data flowing to public surfaces).
Source: docs/superpowers/plans/2026-07-10-closure-master.md (I2).
Primitive: read-verify-export pipeline with gate-provenance enforcement.
"""
import importlib.util
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
EXPORTER = REPO_ROOT / "scripts" / "tools" / "export_app_data.py"


def test_export_app_data_script_exists():
    """export_app_data.py script is present (repo-relative, not a worktree-absolute path)."""
    assert EXPORTER.exists(), f"exporter missing at {EXPORTER}"


def test_export_app_data_imports_and_exposes_api():
    """The exporter loads and exposes its I2 functions (load_gates/build_results_json/main)."""
    spec = importlib.util.spec_from_file_location("export_app_data", EXPORTER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    for fn in ("load_gates", "load_traces", "build_results_json", "main"):
        assert hasattr(mod, fn), f"exporter missing {fn}()"
