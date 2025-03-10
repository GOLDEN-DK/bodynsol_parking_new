#!/usr/bin/env python3
import os
import platform
import subprocess
import sys
import shutil
import requests
import zipfile
import io

def update_chromedriver():
    """
    ChromeDriver를 최신 버전으로 업데이트하는 함수
    """
    print("ChromeDriver 업데이트를 시작합니다...")
    
    # 기존 ChromeDriver 제거 (PATH에 있는 경우)
    try:
        if platform.system() == 'Darwin':  # macOS
            chromedriver_path = '/usr/local/bin/chromedriver'
            if os.path.exists(chromedriver_path):
                print(f"기존 ChromeDriver 제거: {chromedriver_path}")
                os.remove(chromedriver_path)
        elif platform.system() == 'Windows':
            # Windows에서는 PATH에서 chromedriver.exe 찾기
            for path in os.environ['PATH'].split(os.pathsep):
                exe_file = os.path.join(path, 'chromedriver.exe')
                if os.path.exists(exe_file):
                    print(f"기존 ChromeDriver 제거: {exe_file}")
                    os.remove(exe_file)
    except Exception as e:
        print(f"기존 ChromeDriver 제거 중 오류 발생: {str(e)}")
    
    print("ChromeDriver 업데이트가 완료되었습니다.")
    print("이제 프로그램을 실행하면 Selenium이 자동으로 최신 ChromeDriver를 사용합니다.")

if __name__ == "__main__":
    update_chromedriver() 