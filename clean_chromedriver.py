#!/usr/bin/env python3
import os
import shutil
import platform
import sys

def clean_chromedriver_cache():
    """
    ChromeDriver 캐시를 정리하는 함수
    """
    print("ChromeDriver 캐시 정리를 시작합니다...")
    
    # webdriver_manager 캐시 디렉토리 정리
    home_dir = os.path.expanduser("~")
    wdm_dir = os.path.join(home_dir, ".wdm")
    
    if os.path.exists(wdm_dir):
        print(f"webdriver_manager 캐시 디렉토리 삭제: {wdm_dir}")
        try:
            shutil.rmtree(wdm_dir)
            print("삭제 완료")
        except Exception as e:
            print(f"삭제 중 오류 발생: {str(e)}")
    else:
        print(f"webdriver_manager 캐시 디렉토리가 존재하지 않습니다: {wdm_dir}")
    
    # 기존 ChromeDriver 제거 (PATH에 있는 경우)
    try:
        if platform.system() == 'Darwin':  # macOS
            chromedriver_path = '/usr/local/bin/chromedriver'
            if os.path.exists(chromedriver_path):
                print(f"기존 ChromeDriver 제거: {chromedriver_path}")
                os.remove(chromedriver_path)
                print("삭제 완료")
        elif platform.system() == 'Windows':
            # Windows에서는 PATH에서 chromedriver.exe 찾기
            for path in os.environ['PATH'].split(os.pathsep):
                exe_file = os.path.join(path, 'chromedriver.exe')
                if os.path.exists(exe_file):
                    print(f"기존 ChromeDriver 제거: {exe_file}")
                    os.remove(exe_file)
                    print("삭제 완료")
    except Exception as e:
        print(f"기존 ChromeDriver 제거 중 오류 발생: {str(e)}")
    
    print("ChromeDriver 캐시 정리가 완료되었습니다.")
    print("이제 프로그램을 다시 실행해보세요.")

if __name__ == "__main__":
    clean_chromedriver_cache() 