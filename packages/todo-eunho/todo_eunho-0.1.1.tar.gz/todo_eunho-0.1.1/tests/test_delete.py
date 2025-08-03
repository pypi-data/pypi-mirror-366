import subprocess
from pathlib import Path

def test_delete_command():
    project_root = Path(__file__).resolve().parent.parent

    subprocess.run(
        ["python", "-m", "core_code","add", "Delete_Test_Item"],
        cwd=str(project_root)
    )

    result = subprocess.run(
        ["python", "-m", "core_code","delete", "0"],
        capture_output=True,
        text=True,
        cwd=str(project_root)
    )

    # 3. 삭제 성공 메시지 확인
    assert "Deleted: Delete_Test_Item" in result.stdout
