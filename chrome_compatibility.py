#!/usr/bin/env python3
import os
import platform
import subprocess
import sys
import shutil
import requests
import zipfile
import io
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def check_chrome_version():
    """
    설치된 Chrome 브라우저의 버전을 확인하는 함수
    """
    print("Chrome 브라우저 버전을 확인합니다...")
    
    try:
        if platform.system() == 'Windows':
            # Windows에서 Chrome 버전 확인
            try:
                # 레지스트리에서 확인
                import winreg
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Google\Chrome\BLBeacon")
                version, _ = winreg.QueryValueEx(key, "version")
                return version
            except:
                # 실행 파일에서 확인
                try:
                    paths = [
                        os.path.join(os.environ.get('PROGRAMFILES', 'C:\\Program Files'), 'Google\\Chrome\\Application\\chrome.exe'),
                        os.path.join(os.environ.get('PROGRAMFILES(X86)', 'C:\\Program Files (x86)'), 'Google\\Chrome\\Application\\chrome.exe'),
                        os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Google\\Chrome\\Application\\chrome.exe')
                    ]
                    
                    for path in paths:
                        if os.path.exists(path):
                            info = subprocess.check_output(f'wmic datafile where name="{path.replace("\\", "\\\\")}" get Version /value', shell=True)
                            version = info.decode('utf-8').strip().split('=')[1]
                            return version
                except:
                    pass
        
        elif platform.system() == 'Darwin':  # macOS
            try:
                # macOS에서 Chrome 버전 확인
                process = subprocess.Popen(['/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', '--version'], 
                                          stdout=subprocess.PIPE)
                version = process.communicate()[0].decode('UTF-8').replace('Google Chrome ', '').strip()
                return version
            except:
                pass
        
        elif platform.system() == 'Linux':
            try:
                # Linux에서 Chrome 버전 확인
                process = subprocess.Popen(['google-chrome', '--version'], 
                                          stdout=subprocess.PIPE)
                version = process.communicate()[0].decode('UTF-8').replace('Google Chrome ', '').strip()
                return version
            except:
                pass
    
    except Exception as e:
        print(f"Chrome 버전 확인 중 오류 발생: {str(e)}")
    
    return None

def setup_chromedriver():
    """
    ChromeDriver를 설정하는 함수
    """
    print("ChromeDriver 설정을 시작합니다...")
    
    # 기존 캐시 정리
    clean_cache()
    
    try:
        # Chrome 버전 확인
        chrome_version = check_chrome_version()
        if chrome_version:
            print(f"감지된 Chrome 버전: {chrome_version}")
        else:
            print("Chrome 버전을 감지할 수 없습니다. 최신 버전의 ChromeDriver를 사용합니다.")
        
        # ChromeDriver 다운로드 및 설정
        driver_path = ChromeDriverManager().install()
        print(f"ChromeDriver 설치 완료: {driver_path}")
        
        # 테스트 실행
        print("ChromeDriver 테스트 중...")
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        service = Service(driver_path)
        driver = webdriver.Chrome(service=service, options=options)
        driver.quit()
        print("ChromeDriver 테스트 성공!")
        
        return True
    
    except Exception as e:
        print(f"ChromeDriver 설정 중 오류 발생: {str(e)}")
        return False

def clean_cache():
    """
    ChromeDriver 캐시를 정리하는 함수
    """
    print("ChromeDriver 캐시 정리 중...")
    
    # webdriver_manager 캐시 디렉토리 정리
    home_dir = os.path.expanduser("~")
    wdm_dir = os.path.join(home_dir, ".wdm")
    
    if os.path.exists(wdm_dir):
        try:
            shutil.rmtree(wdm_dir)
            print("webdriver_manager 캐시 삭제 완료")
        except Exception as e:
            print(f"캐시 삭제 중 오류 발생: {str(e)}")

def ensure_compatibility():
    """
    Chrome과 ChromeDriver의 호환성을 확인하고 설정하는 함수
    """
    print("Chrome 브라우저와 ChromeDriver 호환성 확인 중...")
    
    # 최대 3번 시도
    for attempt in range(3):
        if setup_chromedriver():
            print("호환성 확인 완료!")
            return True
        else:
            print(f"호환성 확인 실패 (시도 {attempt+1}/3)")
            time.sleep(2)
    
    print("호환성 확인에 실패했습니다. 수동으로 Chrome 브라우저와 ChromeDriver를 확인해주세요.")
    return False

if __name__ == "__main__":
    ensure_compatibility() 