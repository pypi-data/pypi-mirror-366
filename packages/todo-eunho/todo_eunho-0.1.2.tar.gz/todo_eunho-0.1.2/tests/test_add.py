import subprocess
from pathlib import Path

def test_add_command():
    # CLI_dev 프로젝트 루트로 이동
    project_root = Path(__file__).resolve().parent.parent

    # subprocess로 CLI 명령어 실행
    result = subprocess.run(
        ["python", "-m", "core_code","add", "Test_CLI_Item", "--date", "01_AUG_2025", "--time", "12_30"],
        capture_output=True,
        text=True,
        cwd=str(project_root)
    )

    # 디버깅용 출력
    print("STDOUT:", result.stdout)
    print("STDERR:", result.stderr)

    # 성공 메시지 확인
    assert "Todo added successfully!" in result.stdout
