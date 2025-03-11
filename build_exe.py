import os
import sys
import shutil
import subprocess
import platform

def build_exe():
    print("Windows용 실행 파일 빌드를 시작합니다...")
    
    # 빌드 디렉토리 정리
    if os.path.exists("dist"):
        shutil.rmtree("dist")
    if os.path.exists("build"):
        shutil.rmtree("build")
    
    # PyInstaller 명령어 구성
    cmd = [
        "pyinstaller",
        "--name=주차관리시스템",
        "--windowed",  # GUI 애플리케이션
        "--icon=parking_icon.ico",  # 아이콘 파일이 있다면 사용
        "--add-data=chromedriver.exe;.",  # chromedriver.exe 포함
        "--add-data=package_installer.py;.",  # 패키지 설치 스크립트 포함
        "--add-data=chrome_compatibility.py;.",  # 크롬 호환성 스크립트 포함
        "--hidden-import=PyQt6.QtCore",
        "--hidden-import=PyQt6.QtGui",
        "--hidden-import=PyQt6.QtWidgets",
        "--hidden-import=selenium",
        "--hidden-import=webdriver_manager",
        "--hidden-import=pkg_resources",
        "--hidden-import=package_installer",
        "--hidden-import=chrome_compatibility",
        "--clean",
        "main.py"
    ]
    
    # 아이콘 파일이 없으면 해당 옵션 제거
    if not os.path.exists("parking_icon.ico"):
        cmd.remove("--icon=parking_icon.ico")
    
    # chromedriver.exe가 없으면 해당 옵션 제거
    if not os.path.exists("chromedriver.exe"):
        cmd.remove("--add-data=chromedriver.exe;.")
    
    # 명령어 실행
    subprocess.run(cmd)
    
    print("빌드 완료!")
    print("실행 파일은 dist/주차관리시스템 폴더에 있습니다.")
    
    # 추가 파일 복사
    if os.path.exists("requirements.txt"):
        shutil.copy("requirements.txt", "dist/주차관리시스템/")
    
    if os.path.exists("README.md"):
        shutil.copy("README.md", "dist/주차관리시스템/")
    
    if os.path.exists("README_WINDOWS.md"):
        shutil.copy("README_WINDOWS.md", "dist/주차관리시스템/README.txt")
    
    # 패키지 설치 배치 파일 생성
    create_install_batch()
    
    print("필요한 파일 복사 완료!")

def create_install_batch():
    """
    패키지 설치를 위한 배치 파일 생성
    """
    batch_content = """@echo off
echo 주차 관리 시스템 - 패키지 설치
echo.
echo 필요한 패키지를 설치합니다...
echo.

python -m pip install --upgrade pip
python -m pip install PyQt6==6.5.0 selenium==4.18.1 webdriver-manager==4.0.1

echo.
echo 설치가 완료되었습니다. 아무 키나 누르면 창이 닫힙니다.
pause > nul
"""
    
    with open("dist/주차관리시스템/패키지_설치.bat", "w", encoding="utf-8") as f:
        f.write(batch_content)
    
    print("패키지 설치 배치 파일 생성 완료!")

if __name__ == "__main__":
    if platform.system() != "Windows":
        print("이 스크립트는 Windows에서만 실행할 수 있습니다.")
        sys.exit(1)
    
    build_exe() 