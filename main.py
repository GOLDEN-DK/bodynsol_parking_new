import sys
import os
import subprocess
import importlib.util

# 필요한 패키지 확인 및 설치
def check_and_install_packages():
    try:
        # 패키지 설치 모듈 확인
        if importlib.util.find_spec("package_installer") is not None:
            from package_installer import ensure_packages
            ensure_packages()
        else:
            # 패키지 설치 모듈이 없는 경우 기본 패키지 확인
            required_packages = ["PyQt6", "selenium", "webdriver_manager"]
            missing_packages = []
            
            for package in required_packages:
                if importlib.util.find_spec(package) is None:
                    missing_packages.append(package)
            
            if missing_packages:
                print(f"다음 패키지를 설치해야 합니다: {', '.join(missing_packages)}")
                for package in missing_packages:
                    subprocess.check_call([sys.executable, "-m", "pip", "install", package])
                print("필요한 패키지 설치 완료!")
    except Exception as e:
        print(f"패키지 설치 중 오류 발생: {str(e)}")
        print("필요한 패키지를 수동으로 설치해주세요.")

# 패키지 설치 확인 (배포 모드가 아닌 경우에만)
if not getattr(sys, 'frozen', False):
    check_and_install_packages()

# 필요한 모듈 가져오기
try:
    from PyQt6.QtWidgets import QApplication, QMessageBox
    from login import MainWindow
except ImportError as e:
    print(f"필요한 모듈을 가져올 수 없습니다: {str(e)}")
    print("필요한 패키지가 설치되어 있는지 확인해주세요.")
    sys.exit(1)

# 크롬 브라우저 호환성 확인
try:
    from chrome_compatibility import ensure_compatibility
    
    # 실행 파일로 배포된 경우 호환성 확인
    if getattr(sys, 'frozen', False):
        print("배포 모드에서 실행 중...")
        if not ensure_compatibility():
            # 호환성 확인 실패 시 메시지 표시
            app = QApplication(sys.argv)
            QMessageBox.critical(None, "호환성 오류", 
                               "Chrome 브라우저와 ChromeDriver 간의 호환성 문제가 발생했습니다.\n"
                               "최신 버전의 Chrome 브라우저가 설치되어 있는지 확인해주세요.")
            sys.exit(1)
except ImportError:
    print("호환성 모듈을 찾을 수 없습니다. 호환성 검사를 건너뜁니다.")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec()) 