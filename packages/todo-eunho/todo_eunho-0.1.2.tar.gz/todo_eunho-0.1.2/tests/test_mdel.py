import subprocess
from pathlib import Path

def test_mdel_command():
    project_root = Path(__file__).resolve().parent.parent

    # Add multiple items
    subprocess.run(["python", "-m", "core_code", "add", "Multi1"], cwd=str(project_root))
    subprocess.run(["python", "-m", "core_code", "add", "Multi1"], cwd=str(project_root))
    subprocess.run(["python", "-m", "core_code", "add", "Multi1"], cwd=str(project_root))

    result = subprocess.run(
        ["python", "-m", "core_code", "mdel", "0", "1"],
        capture_output=True,
        text=True,
        cwd=str(project_root)
    )

    assert "Deleted:" in result.stdout