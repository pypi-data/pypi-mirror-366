import subprocess
from pathlib import Path

import subprocess
from pathlib import Path

def test_clear_command():
    project_root = Path(__file__).resolve().parent.parent

    subprocess.run(
        ["python", "-m", "core_code", "add", "Temp_Clear"],
        cwd=str(project_root)
    )
    result = subprocess.run(
        ["python", "-m", "core_code", "clear"],
        input="y\n",
        capture_output=True,
        text=True,
        cwd=str(project_root)
    )

    # 3. 결과 확인
    assert "All todo items cleared." in result.stdout
