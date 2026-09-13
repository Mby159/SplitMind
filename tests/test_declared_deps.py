"""Guard: pyproject declarations must match what the package actually imports.

Both directions matter - an undeclared import breaks a fresh install
(`import psutil` inside ollama_manager.get_system_info() had no declaration at
all), while a declared-but-unused dependency is dead weight users install for
nothing (jinja2 / aiohttp / pydantic-settings had zero references anywhere).

Same idea as File-Brain/test_packaging.py, adapted to this repo: only
`splitmind/` and `tests/` are scanned, `examples/` and `packages/` are excluded
because they are known-stale (see packages/README.md).
"""

import ast
import re
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCAN_DIRS = [ROOT / "splitmind", ROOT / "tests"]

DIST_TO_IMPORT = {
    "scikit-learn": "sklearn",
    "python-dotenv": "dotenv",
    "pydantic-settings": "pydantic_settings",
    "pytest-asyncio": "pytest_asyncio",
    "pytest-cov": "pytest_cov",
    "sentence-transformers": "sentence_transformers",
}

# Declared on purpose but never imported by this code.
RUNTIME_ONLY = {
    "pytest": "test runner",
    "pytest-asyncio": "pytest plugin (asyncio_mode = auto)",
    "pytest-cov": "pytest plugin (CI coverage)",
    "black": "formatter used in CI",
    "ruff": "linter used in CI",
    "mypy": "type checker used in CI",
    "python-multipart": "FastAPI form/upload runtime",
    "uvicorn": "ASGI server entry point",
}


def _declared() -> tuple[set[str], set[str]]:
    data = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    project = data["project"]
    own = project["name"].lower()

    def names(reqs):
        out = set()
        for raw in reqs:
            m = re.match(r"([A-Za-z0-9_.\-]+)", raw)
            if not m:
                continue
            name = m.group(1).lower().replace("_", "-")
            if name != own:
                out.add(name)
        return out

    core = names(project.get("dependencies", []))
    extras: set[str] = set()
    for reqs in project.get("optional-dependencies", {}).values():
        extras |= names(reqs)
    return core, extras


def _imported() -> dict[str, set[str]]:
    local = {p.stem for p in (ROOT / "splitmind").rglob("*.py")}
    local |= {"splitmind", "tests", "conftest"}
    found: dict[str, set[str]] = {}
    for base in SCAN_DIRS:
        for path in sorted(base.rglob("*.py")):
            if "__pycache__" in path.parts:
                continue
            tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    mods = [a.name.split(".")[0] for a in node.names]
                elif isinstance(node, ast.ImportFrom):
                    if node.level:
                        continue
                    mods = [(node.module or "").split(".")[0]]
                else:
                    continue
                for mod in mods:
                    if not mod or mod in __import__("sys").stdlib_module_names or mod in local:
                        continue
                    found.setdefault(mod, set()).add(str(path.relative_to(ROOT)))
    return found


def test_every_import_is_declared():
    core, extras = _declared()
    declared_imports = {DIST_TO_IMPORT.get(d, d.replace("-", "_")) for d in core | extras}
    undeclared = {m: sorted(f) for m, f in _imported().items() if m not in declared_imports}

    assert not undeclared, f"imported but not declared in pyproject extras: {undeclared}"


def test_every_declaration_is_used():
    core, extras = _declared()
    imported = set(_imported())
    unused = sorted(
        d for d in core | extras
        if DIST_TO_IMPORT.get(d, d.replace("-", "_")) not in imported and d not in RUNTIME_ONLY
    )

    assert not unused, f"declared but never imported (dead weight): {unused}"
