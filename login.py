import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QLabel, QPushButton, QLineEdit, QMessageBox)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import platform
import shutil
import time

class LoginThread(QThread):
    login_success = pyqtSignal(object)
    login_failed = pyqtSignal(str)
    
    def __init__(self, username, password):
        super().__init__()
        self.username = username
        self.password = password
        
    def run(self):
        try:
            # 크롬 드라이버 설정
            options = webdriver.ChromeOptions()
            # options.add_argument('--headless')  # 필요시 헤드리스 모드 활성화
            options.add_argument('--start-maximized')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            
            # macOS에서는 직접 Chrome 브라우저 사용
            if platform.system() == 'Darwin' and platform.processor() == 'arm':
                # Apple Silicon(M1/M2) Mac용 설정
                options.binary_location = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
                driver = webdriver.Chrome(options=options)
            else:
                # 다른 시스템용 설정
                driver = webdriver.Chrome(options=options)
            
            # 웹사이트 접속
            driver.get("http://kmp0000673.iptime.org/cooperators/home")
            
            # 알림창(alert) 처리
            try:
                # 알림창이 있는지 확인하고 있으면 수락
                alert = driver.switch_to.alert
                alert.accept()
                time.sleep(1)  # 알림창 처리 후 잠시 대기
            except:
                pass  # 알림창이 없으면 넘어감
            
            # 로그인 요소 찾기 및 입력
            wait = WebDriverWait(driver, 10)
            username_field = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="form-login-username"]')))
            password_field = driver.find_element(By.XPATH, '//*[@id="form-login-password"]')
            
            # 아이디와 비밀번호 입력
            username_field.send_keys(self.username)
            password_field.send_keys(self.password)
            
            # 로그인 버튼 클릭
            login_button = driver.find_element(By.XPATH, '//*[@id="form-login"]/div[3]/button')
            login_button.click()
            
            # 알림창(alert) 처리
            try:
                # 알림창이 있는지 확인하고 있으면 수락
                alert = driver.switch_to.alert
                alert_text = alert.text
                alert.accept()
                if "로그인이 필요합니다" in alert_text:
                    # 로그인 실패 시 다시 시도
                    time.sleep(1)  # 잠시 대기
                    username_field = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="form-login-username"]')))
                    password_field = driver.find_element(By.XPATH, '//*[@id="form-login-password"]')
                    username_field.clear()
                    password_field.clear()
                    username_field.send_keys(self.username)
                    password_field.send_keys(self.password)
                    login_button = driver.find_element(By.XPATH, '//*[@id="form-login"]/div[3]/button')
                    login_button.click()
            except:
                pass  # 알림창이 없으면 넘어감
            
            # 로그인 성공 여부 확인 (차량번호 입력 필드가 있는지 확인)
            try:
                wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="visit-lpn"]')))
                self.login_success.emit(driver)
            except Exception as e:
                driver.quit()
                self.login_failed.emit(f"로그인 실패: 로그인 후 화면을 찾을 수 없습니다. 오류: {str(e)}")
                
        except Exception as e:
            self.login_failed.emit(f"로그인 중 오류 발생: {str(e)}")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.driver = None
        self.initUI()
        # 프로그램 시작 시 자동으로 로그인 시도
        self.auto_login()
        
    def initUI(self):
        self.setWindowTitle('주차 관리 시스템')
        self.setGeometry(100, 100, 400, 200)
        
        # 중앙 위젯 설정
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # 상태 레이블
        self.status_label = QLabel('주차 관리 시스템에 접속 중...')
        layout.addWidget(self.status_label)
        
        # 로딩 메시지
        self.loading_label = QLabel('잠시만 기다려주세요...')
        layout.addWidget(self.loading_label)
    
    def auto_login(self):
        # 프로그램 시작 시 자동으로 로그인 시도
        self.status_label.setText('자동 로그인 중...')
        
        # 로그인 스레드 시작
        self.login_thread = LoginThread('바디앤솔', '2728')
        self.login_thread.login_success.connect(self.on_login_success)
        self.login_thread.login_failed.connect(self.on_login_failed)
        self.login_thread.start()
    
    def on_login_success(self, driver):
        self.driver = driver
        self.status_label.setText('로그인 성공!')
        self.open_search_window()
    
    def on_login_failed(self, error_message):
        self.status_label.setText('로그인 실패')
        QMessageBox.critical(self, '로그인 실패', error_message)
        # 로그인 실패 시 재시도 버튼 표시
        retry_button = QPushButton('다시 시도')
        retry_button.clicked.connect(self.auto_login)
        self.centralWidget().layout().addWidget(retry_button)
    
    def open_search_window(self):
        # 여기서 차량 검색 화면으로 전환
        from search import SearchWindow
        self.search_window = SearchWindow(self.driver)
        self.search_window.show()
        self.hide()
    
    def closeEvent(self, event):
        # 창이 닫힐 때 드라이버 종료
        if self.driver:
            self.driver.quit()
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec()) 