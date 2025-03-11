#!/usr/bin/env python3
import os
import sys
import subprocess
import platform
import time
import pkg_resources

def check_package(package_name):
    """
    패키지가 설치되어 있는지 확인하는 함수
    """
    try:
        pkg_resources.get_distribution(package_name)
        return True
    except pkg_resources.DistributionNotFound:
        return False

def install_package(package_name, version=None):
    """
    패키지를 설치하는 함수
    """
    package_spec = package_name
    if version:
        package_spec = f"{package_name}=={version}"
    
    print(f"{package_spec} 설치 중...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_spec])
        print(f"{package_spec} 설치 완료!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"{package_spec} 설치 실패: {str(e)}")
        return False

def install_required_packages():
    """
    필요한 패키지를 설치하는 함수
    """
    print("필요한 패키지 확인 중...")
    
    # 필요한 패키지 목록 (패키지명, 버전)
    required_packages = [
        ("PyQt6", "6.5.0"),
        ("selenium", "4.18.1"),
        ("webdriver-manager", "4.0.1")
    ]
    
    # 설치가 필요한 패키지 확인
    packages_to_install = []
    for package_name, version in required_packages:
        if not check_package(package_name):
            packages_to_install.append((package_name, version))
        else:
            print(f"{package_name} 이미 설치됨")
    
    if not packages_to_install:
        print("모든 필요한 패키지가 이미 설치되어 있습니다.")
        return True
    
    # 패키지 설치 확인
    if packages_to_install:
        print(f"다음 패키지를 설치해야 합니다: {', '.join([p[0] for p in packages_to_install])}")
        
        # 관리자 권한 확인 (Windows)
        if platform.system() == 'Windows':
            try:
                import ctypes
                is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
                if not is_admin:
                    print("일부 패키지는 관리자 권한이 필요할 수 있습니다.")
                    print("설치 중 권한 요청이 표시될 수 있습니다.")
            except:
                pass
        
        # 패키지 설치
        success = True
        for package_name, version in packages_to_install:
            if not install_package(package_name, version):
                success = False
        
        if success:
            print("모든 패키지가 성공적으로 설치되었습니다.")
            return True
        else:
            print("일부 패키지 설치에 실패했습니다.")
            return False
    
    return True

def update_pip():
    """
    pip를 최신 버전으로 업데이트하는 함수
    """
    print("pip 업데이트 중...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
        print("pip 업데이트 완료!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"pip 업데이트 실패: {str(e)}")
        return False

def ensure_packages():
    """
    필요한 패키지가 설치되어 있는지 확인하고 설치하는 함수
    """
    print("패키지 설치 확인을 시작합니다...")
    
    # pip 업데이트
    update_pip()
    
    # 패키지 설치
    return install_required_packages()

if __name__ == "__main__":
    ensure_packages() 