# __main__.py는 패키지 단위로 실행 할 때 사용
# python -m CLI_dev 명령어 실행 시 CLI_dev/ 폴더 내부의 __main__.py를 찾아 실행한다.

from .cli import main

if __name__ == "__main__" :
    main()