import subprocess
from pathlib import Path

def test_show_command():
    project_root = Path(__file__).resolve().parent.parent
    result = subprocess.run(
        ["python", "-m", "core_code", "show"],
        capture_output=True,
        text=True,
        cwd=str(project_root)
    )
    assert "Index" in result.stdout
    assert "Title" in result.stdout