import subprocess
from pathlib import Path

def test_fix_command():
    project_root = Path(__file__).resolve().parent.parent

    # Add item to be fixed
    subprocess.run(["python", "-m", "core_code", "add", "Temp_Fix"], cwd=str(project_root))

    result = subprocess.run(
        ["python", "-m", "core_code", "fix", "0", "--date", "31_JUL_2025", "--time", "09_30"],
        capture_output=True,
        text=True,
        cwd=str(project_root)
    )

    assert "Updated item:" in result.stdout or "updated" in result.stdout