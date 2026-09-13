"""Guard: .env.example must list exactly the env vars the package reads.

Drift here is silent - a user who follows the example either configures
variables nothing reads, or misses the ones that matter. Measured before this
test existed: the example advertised OPENAI_MODEL / ANTHROPIC_MODEL /
KIMI_BASE_URL / KIMI_MODEL (read nowhere) and omitted LOCAL_MODEL_URL /
LOCAL_MODEL_NAME (read by config.py), while the commented local block used the
wrong names LOCAL_BASE_URL / LOCAL_MODEL.
"""

import re
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent.parent / "splitmind"
ENV_EXAMPLE = Path(__file__).resolve().parent.parent / ".env.example"

# matches os.getenv("X"), os.getenv('X', ...), os.environ["X"], os.environ.get("X")
ENV_READ = re.compile(r"""os\.(?:getenv|environ(?:\.get)?)\s*[\(\[]\s*['"]([A-Z0-9_]+)['"]""")


def _vars_read_by_code() -> set[str]:
    found: set[str] = set()
    for path in PACKAGE.rglob("*.py"):
        found |= set(ENV_READ.findall(path.read_text(encoding="utf-8", errors="replace")))
    return found


def _vars_documented() -> set[str]:
    """Only uncommented KEY=VALUE lines count as documented."""
    documented = set()
    for line in ENV_EXAMPLE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        documented.add(line.split("=", 1)[0].strip())
    return documented


def test_env_example_covers_every_variable_the_code_reads():
    missing = _vars_read_by_code() - _vars_documented()

    assert not missing, f"代码会读、但 .env.example 没列出的变量：{sorted(missing)}"


def test_env_example_documents_nothing_the_code_ignores():
    unused = _vars_documented() - _vars_read_by_code()

    assert not unused, (
        f".env.example 列出了、但代码从不读取的变量（设置它们没有效果）：{sorted(unused)}"
    )
