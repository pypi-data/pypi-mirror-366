# .github/scripts/bump_patch.py
import re
from pathlib import Path

pyproject = Path("pyproject.toml")
content = pyproject.read_text(encoding="utf-8")

match = re.search(r'version\s*=\s*"(\d+)\.(\d+)\.(\d+)"', content)
if not match:
    raise SystemExit("Could not find version string in pyproject.toml!")

major, minor, patch = map(int, match.groups())
patch += 1

new_version = f'{major}.{minor}.{patch}'
new_content = re.sub(
    r'version\s*=\s*"\d+\.\d+\.\d+"',
    f'version = "{new_version}"',
    content
)

pyproject.write_text(new_content, encoding="utf-8")
print(f"Bumped version to {new_version}")