"""prabodha CLI — the H4 application surface: one entrypoint over the toolkit.
Concept: the doctrine as a usable instrument (clean external surface, RULES R8 — the
engineering-gloss column only). Subcommands route to the tested module CLIs.
Source: docs/h4_plugin_architecture.md phase 1.
Primitive: `prabodha <cmd> [args...]` -> module main(argv). Stdlib dispatch only.

  prabodha lens-fit   --model M.yaml --lens L.yaml --out lens.pt [--resume]
  prabodha lens-eval  --model M.yaml --lens-file lens.pt --exp E.yaml --out gate.json
  prabodha lens-vis   --model M.yaml --lens-file lens.pt --prompt "..." --out page.html
  prabodha steer      --model M.yaml --mid-lens lens.pt --exp E.yaml --out gate.json
  prabodha research   [--menu menu.yaml] [--propose]
  prabodha figures    (regenerate paper/HTML figures from gates)
"""
import sys


def main() -> None:
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print(__doc__)
        raise SystemExit(0)
    cmd, argv = sys.argv[1], sys.argv[2:]
    if cmd == "lens-fit":
        from prabodha.lens import fit_cli
        sys.argv = ["fit_cli"] + argv
        fit_cli.main()
    elif cmd == "lens-eval":
        from prabodha.lens import e1_cli
        e1_cli.main(argv)
    elif cmd == "lens-vis":
        from prabodha.lens import vis_cli
        vis_cli.main(argv)
    elif cmd == "steer":
        from prabodha.steering import e4_cli
        e4_cli.main(argv)
    elif cmd == "research":
        from prabodha.efe import runner
        runner.main(argv)
    elif cmd == "figures":
        import runpy
        from pathlib import Path
        script = Path(__file__).resolve().parents[2] / "scripts/tools/make_figures.py"
        runpy.run_path(str(script), run_name="__main__")
    else:
        print(f"unknown command: {cmd}\n{__doc__}")
        raise SystemExit(2)


if __name__ == "__main__":
    main()
