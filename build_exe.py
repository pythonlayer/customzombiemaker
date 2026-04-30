import argparse
import importlib.util
import os
import subprocess
import sys
from pathlib import Path


WINDOWED_SCRIPT_NAMES = {"list_builder.py", "mic_to_midi_app.py"}
DEFAULT_EXE_NAMES = {
    "list_builder.py": "ELM List Generator",
}
COMMON_DATA_DIRS = ("assets", "css", "js")
COMMON_DATA_FILES = ("codenames",)
COMMON_DATA_GLOBS = ("*.json",)


def pyinstaller_is_installed():
    return importlib.util.find_spec("PyInstaller") is not None


def probe_tkinter():
    try:
        import tkinter

        tkinter.Tcl()
        return True, ""
    except Exception as exc:
        return False, str(exc).strip()


def infer_mode(target_path):
    if target_path.name.lower() in WINDOWED_SCRIPT_NAMES:
        return "windowed"

    try:
        source = target_path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return "console"

    if "import tkinter" in source or "from tkinter" in source:
        return "windowed"
    return "console"


def collect_common_data(project_dir):
    collected = []
    seen = set()

    for pattern in COMMON_DATA_GLOBS:
        for path in sorted(project_dir.glob(pattern)):
            resolved = path.resolve()
            if resolved in seen or not path.is_file():
                continue
            collected.append((path, "."))
            seen.add(resolved)

    for name in COMMON_DATA_FILES:
        path = project_dir / name
        resolved = path.resolve()
        if path.exists() and resolved not in seen:
            collected.append((path, "."))
            seen.add(resolved)

    for name in COMMON_DATA_DIRS:
        path = project_dir / name
        resolved = path.resolve()
        if path.exists() and path.is_dir() and resolved not in seen:
            collected.append((path, name))
            seen.add(resolved)

    return collected


def build_pyinstaller_command(args, target_path):
    project_dir = target_path.parent
    name = args.name or DEFAULT_EXE_NAMES.get(target_path.name.lower(), target_path.stem)
    mode = args.mode
    if mode == "auto":
        mode = infer_mode(target_path)

    build_root = project_dir / "build"
    workpath = args.workpath.resolve() if args.workpath else build_root / "pyinstaller"
    specpath = args.specpath.resolve() if args.specpath else build_root / "specs"
    distpath = args.distpath.resolve() if args.distpath else project_dir / "dist"

    command = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--clean",
        "--name",
        name,
        "--specpath",
        str(specpath),
        "--workpath",
        str(workpath),
        "--distpath",
        str(distpath),
    ]

    command.append("--onefile" if args.onefile else "--onedir")
    command.append("--windowed" if mode == "windowed" else "--console")

    if args.icon:
        command.extend(["--icon", str(args.icon.resolve())])

    if args.add_data:
        for raw_pair in args.add_data:
            command.extend(["--add-data", raw_pair])

    if args.hidden_import:
        for module_name in args.hidden_import:
            command.extend(["--hidden-import", module_name])

    if not args.no_common_data:
        for source_path, dest_name in collect_common_data(project_dir):
            command.extend(["--add-data", f"{source_path}{os.pathsep}{dest_name}"])

    command.append(str(target_path))
    return command, mode, distpath, name


def parse_args():
    parser = argparse.ArgumentParser(
        description="Build a Windows .exe for one of the project Python entry points using PyInstaller."
    )
    parser.add_argument(
        "target",
        help="Python entry script to package, for example list_builder.py or level_generator.py.",
    )
    parser.add_argument("--name", help="Override the output executable name.")
    parser.add_argument(
        "--mode",
        choices=("auto", "console", "windowed"),
        default="auto",
        help="Build mode. Auto picks windowed for Tkinter apps and console otherwise.",
    )
    parser.add_argument(
        "--onefile",
        action="store_true",
        help="Build a single-file executable instead of the default one-folder build.",
    )
    parser.add_argument("--icon", type=Path, help="Optional .ico file for the executable.")
    parser.add_argument(
        "--distpath",
        type=Path,
        help="Optional output directory for the finished build. Default: ./dist",
    )
    parser.add_argument(
        "--workpath",
        type=Path,
        help="Optional temporary PyInstaller work directory. Default: ./build/pyinstaller",
    )
    parser.add_argument(
        "--specpath",
        type=Path,
        help="Optional directory for the generated .spec file. Default: ./build/specs",
    )
    parser.add_argument(
        "--add-data",
        action="append",
        default=[],
        metavar="SRC;DEST",
        help="Extra PyInstaller data mapping, for example --add-data \"extra.json;.\"",
    )
    parser.add_argument(
        "--hidden-import",
        action="append",
        default=[],
        metavar="MODULE",
        help="Extra hidden import for PyInstaller. Repeat as needed.",
    )
    parser.add_argument(
        "--no-common-data",
        action="store_true",
        help="Do not auto-bundle the project's json/data folders.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the PyInstaller command without running it.",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    target_path = Path(args.target).resolve()

    if not target_path.exists():
        raise SystemExit(f"Target script not found: {target_path}")
    if target_path.suffix.lower() != ".py":
        raise SystemExit(f"Target must be a .py file: {target_path}")
    if not pyinstaller_is_installed():
        raise SystemExit("PyInstaller is not installed. Run: pip install pyinstaller")
    if args.icon and not args.icon.exists():
        raise SystemExit(f"Icon file not found: {args.icon.resolve()}")

    command, resolved_mode, distpath, name = build_pyinstaller_command(args, target_path)
    tkinter_ok, tkinter_error = True, ""
    if resolved_mode == "windowed":
        tkinter_ok, tkinter_error = probe_tkinter()

    print(f"Target : {target_path.name}")
    print(f"Mode   : {resolved_mode}")
    print(f"Bundle : {'onefile' if args.onefile else 'onedir'}")
    print(f"Output : {distpath / name}")
    if resolved_mode == "windowed" and not tkinter_ok:
        print("")
        print("WARNING: Tcl/Tk is not usable in this Python install.", file=sys.stderr)
        print("The build may finish, but the GUI exe can still fail at launch.", file=sys.stderr)
        print(tkinter_error, file=sys.stderr)
    print("")
    print("PyInstaller command:")
    print(" ".join(f'"{part}"' if " " in part else part for part in command))

    if args.dry_run:
        return

    subprocess.run(command, check=True, cwd=str(target_path.parent))

    exe_suffix = ".exe"
    if args.onefile:
        built_exe = distpath / f"{name}{exe_suffix}"
    else:
        built_exe = distpath / name / f"{name}{exe_suffix}"

    print("")
    print(f"Build finished: {built_exe}")


if __name__ == "__main__":
    main()
