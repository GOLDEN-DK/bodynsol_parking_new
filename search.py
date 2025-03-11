import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                            QLabel, QPushButton, QLineEdit, QMessageBox, QGroupBox, QGridLayout,
                            QScrollArea)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QPixmap
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import requests
from io import BytesIO
import platform
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import shutil
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import ElementClickInterceptedException, StaleElementReferenceException

class SearchThread(QThread):
    search_success = pyqtSignal(str, str, list)  # 차량번호, 이미지URL, 기존 주차권 목록
    search_failed = pyqtSignal(str)
    search_timeout = pyqtSignal()  # 검색 시간 초과 시그널 추가
    
    def __init__(self, driver, car_number):
        super().__init__()
        self.driver = driver
        self.car_number = car_number
        self.timeout = 3  # 3초 타임아웃 설정
        
    def run(self):
        try:
            wait = WebDriverWait(self.driver, self.timeout)
            
            # 차량번호 입력 필드 찾기
            car_number_field = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="visit-lpn"]')))
            
            # 이전 검색 결과가 있다면 초기화
            try:
                # 대화상자가 있는지 확인하고 닫기
                dialogs = self.driver.find_elements(By.CSS_SELECTOR, '.dialog-holder')
                for dialog in dialogs:
                    if dialog.is_displayed():
                        # 대화상자의 닫기 버튼 찾기 및 클릭
                        close_buttons = dialog.find_elements(By.CSS_SELECTOR, '.btn-close')
                        for btn in close_buttons:
                            try:
                                btn.click()
                                time.sleep(0.5)
                            except:
                                pass
                
                # 초기화 버튼 찾기 및 클릭
                init_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="btn-init"]')))
                # JavaScript로 클릭 실행
                self.driver.execute_script("arguments[0].click();", init_button)
                time.sleep(1)  # 초기화 후 잠시 대기
                
                # 초기화 후 다시 차량번호 입력 필드 찾기
                car_number_field = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="visit-lpn"]')))
            except Exception as e:
                print(f"초기화 버튼 클릭 중 오류 (무시됨): {str(e)}")
                pass  # 초기화 버튼이 없으면 넘어감
            
            # 차량번호 입력
            car_number_field.clear()
            car_number_field.send_keys(self.car_number)
            
            # 조회 버튼 클릭
            search_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="btn-find"]')))
            search_button.click()
            
            # 검색 시작 시간 기록
            start_time = time.time()
            
            # 검색 결과 확인 (차량번호가 표시되는지 확인)
            try:
                # 검색 결과가 나타날 때까지 대기 (짧은 타임아웃 설정)
                short_wait = WebDriverWait(self.driver, self.timeout)
                short_wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="page-view"]/table/tbody/tr[1]/td[2]')))
                
                # 차량번호 확인
                car_number_result = self.driver.find_element(By.XPATH, '//*[@id="page-view"]/table/tbody/tr[1]/td[2]').text
                
                # 차량 이미지 URL 가져오기
                try:
                    img_element = self.driver.find_element(By.XPATH, '//*[@id="page-view"]/table/tbody/tr[8]/td/img')
                    img_url = img_element.get_attribute('src')
                    
                    # 기존 주차권 확인 - 정확한 방식
                    existing_tickets = []
                    
                    # 취소 버튼 확인 - 취소 버튼의 존재 여부로 주차권 확인
                    cancel_buttons = self.driver.find_elements(By.CSS_SELECTOR, '.btn-cancel-visit-coupon')
                    print(f"취소 버튼 {len(cancel_buttons)}개 발견")
                    
                    if len(cancel_buttons) > 0:
                        # 주차권 정보가 있는 div 요소 찾기 (qbox-filter-field 클래스)
                        try:
                            # 정확한 XPath를 사용하여 주차권 정보 찾기
                            filter_fields = self.driver.find_elements(By.XPATH, '//div[contains(@class, "qbox-filter-field")]')
                            
                            for field in filter_fields:
                                try:
                                    # 취소 버튼이 있는 div만 선택 (실제 주차권)
                                    cancel_btns = field.find_elements(By.CSS_SELECTOR, '.btn-cancel-visit-coupon')
                                    if len(cancel_btns) > 0:
                                        field_text = field.text.strip()
                                        if field_text:
                                            print(f"주차권 텍스트: {field_text}")
                                            # X 버튼 텍스트 제거
                                            field_text = field_text.replace('X', '').strip()
                                            existing_tickets.append(field_text)
                                except Exception as e:
                                    print(f"필드 내 취소 버튼 확인 중 오류: {str(e)}")
                        except Exception as e:
                            print(f"주차권 필드 확인 중 오류: {str(e)}")
                    
                    # 주차권이 발견되지 않았지만 취소 버튼이 있는 경우 (텍스트 추출 실패)
                    if len(cancel_buttons) > 0 and not existing_tickets:
                        print("취소 버튼은 있지만 주차권 텍스트를 가져오지 못함")
                        
                        # 페이지 소스에서 주차권 정보 확인
                        page_source = self.driver.page_source
                        
                        # 취소 버튼 개수에 따라 주차권 추가
                        for i in range(len(cancel_buttons)):
                            if i == 0 and "1시간(유료)" in page_source:
                                existing_tickets.append("1시간(유료) / 바디앤솔 필라테스")
                                print("페이지 소스에서 1시간 주차권 발견")
                            elif i == 1 and "30분(유료)" in page_source:
                                existing_tickets.append("30분(유료) / 바디앤솔 필라테스")
                                print("페이지 소스에서 30분 주차권 발견")
                    
                    # 검색 성공 시그널 발생
                    self.search_success.emit(car_number_result, img_url, existing_tickets)
                except Exception as e:
                    # 시간 체크 - 3초 이상 지났는지 확인
                    if time.time() - start_time >= self.timeout:
                        self.search_timeout.emit()
                    else:
                        self.search_failed.emit(f"차량 이미지를 찾을 수 없습니다. 오류: {str(e)}")
            except Exception as e:
                # 시간 체크 - 3초 이상 지났는지 확인
                if time.time() - start_time >= self.timeout:
                    self.search_timeout.emit()
                else:
                    self.search_failed.emit(f"차량 검색 결과를 찾을 수 없습니다. 오류: {str(e)}")
                
        except Exception as e:
            # 시간 체크 - 3초 이상 지났는지 확인
            if hasattr(self, 'start_time') and time.time() - self.start_time >= self.timeout:
                self.search_timeout.emit()
            else:
                self.search_failed.emit(f"차량 검색 중 오류 발생: {str(e)}")

class ParkingTimeThread(QThread):
    success = pyqtSignal(str)
    failed = pyqtSignal(str)
    
    def __init__(self, driver, minutes):
        super().__init__()
        self.driver = driver
        self.minutes = minutes
        
    def run(self):
        try:
            wait = WebDriverWait(self.driver, 10)
            
            # 대화상자가 있는지 확인하고 닫기
            dialogs = self.driver.find_elements(By.CSS_SELECTOR, '.dialog-holder')
            for dialog in dialogs:
                if dialog.is_displayed():
                    # 대화상자의 닫기 버튼 찾기 및 클릭
                    close_buttons = dialog.find_elements(By.CSS_SELECTOR, '.btn-close')
                    for btn in close_buttons:
                        try:
                            btn.click()
                            time.sleep(0.5)
                        except:
                            pass
            
            # 선택된 시간에 따라 버튼 클릭
            if self.minutes == 30 or self.minutes == 90:
                # 30분 버튼 클릭
                min30_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="page-view"]/table/tbody/tr[7]/td/button')))
                # JavaScript로 클릭 실행
                self.driver.execute_script("arguments[0].click();", min30_button)
                time.sleep(1)  # 클릭 후 잠시 대기
            
            if self.minutes == 60 or self.minutes == 90:
                # 1시간 버튼 클릭
                hour1_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="page-view"]/table/tbody/tr[5]/td/button')))
                # JavaScript로 클릭 실행
                self.driver.execute_script("arguments[0].click();", hour1_button)
                time.sleep(1)  # 클릭 후 잠시 대기
            
            # 선택된 시간 표시
            time_text = ""
            if self.minutes == 30:
                time_text = "30분"
            elif self.minutes == 60:
                time_text = "1시간"
            elif self.minutes == 90:
                time_text = "1시간 30분"
            
            # 선택 확인 (선택된 주차권 정보가 표시되는지 확인)
            try:
                # 선택된 주차권 정보 확인
                coupon_fields = self.driver.find_elements(By.CSS_SELECTOR, '.qbox-filter-field')
                if len(coupon_fields) > 0:
                    self.success.emit(time_text)
                else:
                    self.failed.emit(f"{time_text} 주차권 선택이 확인되지 않았습니다.")
            except Exception as e:
                self.failed.emit(f"주차권 선택 확인 중 오류 발생: {str(e)}")
                
        except Exception as e:
            self.failed.emit(f"주차권 선택 중 오류 발생: {str(e)}")

class ClearTicketsThread(QThread):
    success = pyqtSignal()
    failed = pyqtSignal(str)
    
    def __init__(self, driver):
        super().__init__()
        self.driver = driver
        
    def run(self):
        try:
            wait = WebDriverWait(self.driver, 10)
            
            # 대화상자가 있는지 확인하고 닫기
            dialogs = self.driver.find_elements(By.CSS_SELECTOR, '.dialog-holder')
            for dialog in dialogs:
                if dialog.is_displayed():
                    # 대화상자의 닫기 버튼 찾기 및 클릭
                    close_buttons = dialog.find_elements(By.CSS_SELECTOR, '.btn-close')
                    for btn in close_buttons:
                        try:
                            btn.click()
                            time.sleep(0.5)
                        except:
                            pass
            
            # 모든 주차권을 삭제할 때까지 반복
            max_attempts = 10  # 최대 시도 횟수 설정
            for attempt in range(max_attempts):
                # 선택된 주차권 취소 버튼 찾기
                cancel_buttons = self.driver.find_elements(By.CSS_SELECTOR, '.btn-cancel-visit-coupon')
                
                # 더 이상 취소할 주차권이 없으면 종료
                if len(cancel_buttons) == 0:
                    break
                
                # 첫 번째 취소 버튼 클릭
                try:
                    # JavaScript로 클릭 실행
                    self.driver.execute_script("arguments[0].click();", cancel_buttons[0])
                    time.sleep(1)  # 클릭 후 대기 시간 증가
                    
                    # 확인 대화상자가 나타나면 확인 버튼 클릭
                    try:
                        alert = self.driver.switch_to.alert
                        alert.accept()
                        time.sleep(1)  # 확인 후 대기 시간 증가
                    except:
                        pass
                    
                    # 대화상자가 있는지 확인하고 닫기
                    dialogs = self.driver.find_elements(By.CSS_SELECTOR, '.dialog-holder')
                    for dialog in dialogs:
                        if dialog.is_displayed():
                            # 대화상자의 닫기 버튼 찾기 및 클릭
                            close_buttons = dialog.find_elements(By.CSS_SELECTOR, '.btn-close')
                            for btn in close_buttons:
                                try:
                                    btn.click()
                                    time.sleep(0.5)
                                except:
                                    pass
                except Exception as e:
                    print(f"이용권 취소 버튼 클릭 중 오류: {str(e)}")
            
            # 초기화 버튼 찾기 및 클릭
            init_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="btn-init"]')))
            # JavaScript로 클릭 실행
            self.driver.execute_script("arguments[0].click();", init_button)
            time.sleep(1)  # 초기화 후 잠시 대기
            
            # 최종 확인: 모든 주차권이 삭제되었는지 확인
            remaining_buttons = self.driver.find_elements(By.CSS_SELECTOR, '.btn-cancel-visit-coupon')
            if len(remaining_buttons) > 0:
                self.failed.emit("일부 이용권이 삭제되지 않았습니다. 다시 시도해주세요.")
            else:
                self.success.emit()
                
        except Exception as e:
            self.failed.emit(f"이용권 초기화 중 오류 발생: {str(e)}")

class SearchWindow(QMainWindow):
    def __init__(self, driver):
        super().__init__()
        self.driver = driver
        self.existing_tickets = []
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle('주차 관리 시스템 - 차량 검색')
        # 전체화면으로 설정
        self.showMaximized()
        
        # 스타일 설정 - 현대적인 흰색 테마
        self.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #ffffff;
                color: #333333;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QGroupBox {
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                margin-top: 12px;
                font-weight: bold;
                background-color: #ffffff;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                color: #2c3e50;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
                min-height: 30px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
            }
            QLineEdit {
                border: 3px solid #3498db;
                border-radius: 10px;
                padding: 15px;
                background-color: #f0f8ff;
                min-height: 70px;
                font-size: 40px;
                font-weight: bold;
                color: #2c3e50;
            }
            QLabel {
                color: #2c3e50;
                font-size: 14px;
            }
            QMessageBox {
                background-color: #ffffff;
            }
            QPushButton#keypad_button {
                background-color: #2c3e50;
                color: white;
                border: 1px solid #34495e;
                font-size: 36px;
                font-weight: bold;
                min-height: 100px;
                min-width: 100px;
                border-radius: 10px;
            }
            QPushButton#keypad_button:hover {
                background-color: #34495e;
                border: 2px solid #3498db;
            }
            QPushButton#time_button {
                background-color: #27ae60;
                min-width: 150px;
                min-height: 70px;
                font-size: 20px;
                font-weight: bold;
                border-radius: 8px;
            }
            QPushButton#time_button:hover {
                background-color: #2ecc71;
                border: 2px solid #27ae60;
            }
            QPushButton#clear_button {
                background-color: #e74c3c;
                font-size: 20px;
                font-weight: bold;
                min-height: 60px;
                min-width: 200px;
                border-radius: 8px;
            }
            QPushButton#clear_button:hover {
                background-color: #c0392b;
                border: 2px solid #e74c3c;
            }
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)
        
        # 중앙 위젯 설정
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 30, 30, 30)
        
        # 스크롤 영역 생성
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QScrollArea.Shape.NoFrame)
        
        # 스크롤 영역에 들어갈 컨텐츠 위젯
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(20)
        
        # 검색 그룹
        search_group = QGroupBox("차량 검색")
        search_layout = QVBoxLayout()
        search_layout.setSpacing(20)
        
        # 차량번호 입력 레이아웃
        input_layout = QVBoxLayout()
        self.car_number_label = QLabel('차량번호 뒤 4자리:')
        self.car_number_label.setStyleSheet("font-size: 20px; font-weight: bold;")
        
        self.car_number_input = QLineEdit()
        self.car_number_input.setPlaceholderText('예: 1234')
        self.car_number_input.setMaxLength(4)
        self.car_number_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.car_number_input.setStyleSheet("""
            font-size: 48px; 
            font-weight: bold;
            border: 4px solid #3498db;
            border-radius: 15px;
            padding: 20px;
            margin: 15px 0;
            background-color: #f0f8ff;
            color: #2c3e50;
        """)
        self.car_number_input.textChanged.connect(self.on_text_changed)
        
        input_layout.addWidget(self.car_number_label)
        input_layout.addWidget(self.car_number_input)
        
        search_layout.addLayout(input_layout)
        
        # 키패드 추가
        keypad_layout = QGridLayout()
        keypad_layout.setSpacing(10)
        
        # 숫자 버튼 생성 (1-9)
        for i in range(9):
            row = i // 3
            col = i % 3
            num_button = QPushButton(str(i + 1))
            num_button.setObjectName("keypad_button")
            num_button.clicked.connect(lambda _, digit=i+1: self.add_digit(str(digit)))
            keypad_layout.addWidget(num_button, row, col)
        
        # 0 버튼
        zero_button = QPushButton("0")
        zero_button.setObjectName("keypad_button")
        zero_button.clicked.connect(lambda: self.add_digit("0"))
        keypad_layout.addWidget(zero_button, 3, 1)
        
        # 지우기 버튼
        clear_button = QPushButton("C")
        clear_button.setObjectName("keypad_button")
        clear_button.setStyleSheet("""
            QPushButton#keypad_button {
                background-color: #c0392b;
                color: white;
                font-size: 36px;
                font-weight: bold;
                min-height: 100px;
                min-width: 100px;
            }
            QPushButton#keypad_button:hover {
                background-color: #e74c3c;
                border: 2px solid #c0392b;
            }
        """)
        clear_button.clicked.connect(self.clear_input)
        keypad_layout.addWidget(clear_button, 3, 0)
        
        # 백스페이스 버튼
        backspace_button = QPushButton("←")
        backspace_button.setObjectName("keypad_button")
        backspace_button.setStyleSheet("""
            QPushButton#keypad_button {
                background-color: #d35400;
                color: white;
                font-size: 36px;
                font-weight: bold;
                min-height: 100px;
                min-width: 100px;
            }
            QPushButton#keypad_button:hover {
                background-color: #e67e22;
                border: 2px solid #d35400;
            }
        """)
        backspace_button.clicked.connect(self.backspace)
        keypad_layout.addWidget(backspace_button, 3, 2)
        
        search_layout.addLayout(keypad_layout)
        
        # 상태 레이블
        self.status_label = QLabel('')
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #3498db; margin-top: 10px;")
        search_layout.addWidget(self.status_label)
        
        search_group.setLayout(search_layout)
        scroll_layout.addWidget(search_group)
        
        # 검색 결과 그룹
        result_group = QGroupBox("검색 결과")
        result_layout = QVBoxLayout()
        result_layout.setSpacing(10)
        
        # 차량 정보 레이블
        self.car_info_label = QLabel('차량 정보: ')
        self.car_info_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        result_layout.addWidget(self.car_info_label)
        
        # 차량 이미지 레이블
        self.car_image_label = QLabel('차량 이미지')
        self.car_image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.car_image_label.setMinimumHeight(200)
        self.car_image_label.setStyleSheet("border: 1px solid #e0e0e0; border-radius: 4px; background-color: #f8f9fa;")
        result_layout.addWidget(self.car_image_label)
        
        # 기존 주차권 정보 레이블
        self.existing_tickets_label = QLabel('기존 이용권: 없음')
        self.existing_tickets_label.setStyleSheet("font-size: 14px;")
        result_layout.addWidget(self.existing_tickets_label)
        
        # 주차권 선택 버튼 그룹
        parking_group = QGroupBox("주차권 선택")
        parking_layout = QHBoxLayout()
        parking_layout.setSpacing(20)
        
        self.btn_30min = QPushButton("30분")
        self.btn_30min.setObjectName("time_button")
        self.btn_1hour = QPushButton("1시간")
        self.btn_1hour.setObjectName("time_button")
        self.btn_1hour30min = QPushButton("1시간 30분")
        self.btn_1hour30min.setObjectName("time_button")
        
        self.btn_30min.clicked.connect(lambda: self.select_parking_time(30))
        self.btn_1hour.clicked.connect(lambda: self.select_parking_time(60))
        self.btn_1hour30min.clicked.connect(lambda: self.select_parking_time(90))
        
        # 처음에는 주차권 버튼 비활성화
        self.btn_30min.setEnabled(False)
        self.btn_1hour.setEnabled(False)
        self.btn_1hour30min.setEnabled(False)
        
        parking_layout.addWidget(self.btn_30min)
        parking_layout.addWidget(self.btn_1hour)
        parking_layout.addWidget(self.btn_1hour30min)
        
        parking_group.setLayout(parking_layout)
        result_layout.addWidget(parking_group)
        
        # 선택된 주차권 정보
        self.selected_time_label = QLabel("선택된 시간: ")
        self.selected_time_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        self.selected_time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        result_layout.addWidget(self.selected_time_label)
        
        result_group.setLayout(result_layout)
        scroll_layout.addWidget(result_group)
        
        # 버튼 그룹 (이용권 초기화 및 다시 검색)
        button_layout = QHBoxLayout()
        button_layout.setSpacing(20)
        
        # 이용권 초기화 버튼
        self.reset_button = QPushButton("이용권 초기화")
        self.reset_button.setObjectName("clear_button")
        self.reset_button.clicked.connect(self.clear_tickets)
        button_layout.addWidget(self.reset_button)
        
        # 다시 검색 버튼
        self.new_search_button = QPushButton("다시 검색")
        self.new_search_button.setStyleSheet("""
            background-color: #3498db;
            color: white;
            font-size: 20px;
            font-weight: bold;
            min-height: 60px;
            min-width: 200px;
            border-radius: 8px;
        """)
        self.new_search_button.clicked.connect(self.reset_search)
        button_layout.addWidget(self.new_search_button)
        
        scroll_layout.addLayout(button_layout)
        
        # 스크롤 영역 설정 완료
        scroll_area.setWidget(scroll_content)
        main_layout.addWidget(scroll_area)
        
        # 검색 시도 횟수 초기화
        self.search_attempts = 0
        self.max_search_attempts = 3  # 최대 재시도 횟수
    
    # 키패드 관련 함수 추가
    def add_digit(self, digit):
        current_text = self.car_number_input.text()
        if len(current_text) < 4:
            self.car_number_input.setText(current_text + digit)
    
    def clear_input(self):
        self.car_number_input.clear()
    
    def backspace(self):
        current_text = self.car_number_input.text()
        if current_text:
            self.car_number_input.setText(current_text[:-1])
    
    # 텍스트 변경 시 자동 검색 기능
    def on_text_changed(self, text):
        if len(text) == 4 and text.isdigit():
            self.search_car()
    
    def search_car(self):
        car_number = self.car_number_input.text().strip()
        
        if not car_number or len(car_number) != 4 or not car_number.isdigit():
            QMessageBox.warning(self, '입력 오류', '차량번호 뒤 4자리를 정확히 입력하세요.')
            return
        
        self.status_label.setText('차량 검색 중...')
        # 주차권 버튼 비활성화
        self.btn_30min.setEnabled(False)
        self.btn_1hour.setEnabled(False)
        self.btn_1hour30min.setEnabled(False)
        
        # 검색 시도 횟수 초기화
        self.search_attempts = 0
        self.max_search_attempts = 3  # 최대 재시도 횟수
        
        # 검색 스레드 시작
        self.start_search_thread(car_number)
    
    def start_search_thread(self, car_number):
        self.search_thread = SearchThread(self.driver, car_number)
        self.search_thread.search_success.connect(self.on_search_success)
        self.search_thread.search_failed.connect(self.on_search_failed)
        self.search_thread.search_timeout.connect(self.on_search_timeout)
        self.search_thread.start()
    
    def on_search_success(self, car_number, img_url, existing_tickets):
        self.status_label.setText('차량 검색 성공!')
        # 주차권 버튼 활성화
        self.btn_30min.setEnabled(True)
        self.btn_1hour.setEnabled(True)
        self.btn_1hour30min.setEnabled(True)
        
        # 차량 정보 표시
        self.car_info_label.setText(f'차량 정보: {car_number}')
        
        # 차량 이미지 표시
        try:
            response = requests.get(img_url)
            img_data = BytesIO(response.content)
            pixmap = QPixmap()
            pixmap.loadFromData(img_data.getvalue())
            
            # 이미지 크기 조정
            pixmap = pixmap.scaled(400, 300, Qt.AspectRatioMode.KeepAspectRatio)
            self.car_image_label.setPixmap(pixmap)
        except Exception as e:
            self.car_image_label.setText(f"이미지 로드 실패: {str(e)}")
        
        # 기존 주차권 정보 표시
        self.existing_tickets = existing_tickets
        if existing_tickets:
            tickets_text = "\n".join(existing_tickets)
            self.existing_tickets_label.setText(f'기존 이용권:\n{tickets_text}')
            print(f"표시할 주차권 목록: {existing_tickets}")
            
            # 주차권이 이미 있으면 버튼 비활성화
            self.btn_30min.setEnabled(False)
            self.btn_1hour.setEnabled(False)
            self.btn_1hour30min.setEnabled(False)
            
            # 선택된 시간 표시
            total_minutes = 0
            for ticket in existing_tickets:
                if "30분" in ticket:
                    total_minutes += 30
                elif "1시간" in ticket:
                    total_minutes += 60
            
            time_text = ""
            if total_minutes == 30:
                time_text = "30분"
            elif total_minutes == 60:
                time_text = "1시간"
            elif total_minutes == 90:
                time_text = "1시간 30분"
                
            self.selected_time_label.setText(f"선택된 시간: {time_text}")
            
            # 주차권이 있음을 알림
            QMessageBox.information(self, '이용권 확인', f'이 차량에는 이미 {time_text} 이용권이 발급되어 있습니다.')
        else:
            self.existing_tickets_label.setText('기존 이용권: 없음')
            
            # 주차권이 없으면 버튼 활성화
            self.btn_30min.setEnabled(True)
            self.btn_1hour.setEnabled(True)
            self.btn_1hour30min.setEnabled(True)
            
            # 선택된 시간 초기화
            self.selected_time_label.setText("선택된 시간: ")
    
    def on_search_failed(self, error_message):
        self.status_label.setText('차량 검색 실패')
        # 주차권 버튼 활성화
        self.btn_30min.setEnabled(False)
        self.btn_1hour.setEnabled(False)
        self.btn_1hour30min.setEnabled(False)
        QMessageBox.critical(self, '검색 실패', error_message)
    
    def select_parking_time(self, minutes):
        self.status_label.setText('주차권 선택 중...')
        self.btn_30min.setEnabled(False)
        self.btn_1hour.setEnabled(False)
        self.btn_1hour30min.setEnabled(False)
        
        # 주차권 선택 스레드 시작
        self.parking_thread = ParkingTimeThread(self.driver, minutes)
        self.parking_thread.success.connect(self.on_parking_success)
        self.parking_thread.failed.connect(self.on_parking_failed)
        self.parking_thread.start()
    
    def on_parking_success(self, time_text):
        self.status_label.setText('주차권 선택 완료!')
        self.selected_time_label.setText(f"선택된 시간: {time_text}")
        
        # 선택 완료 메시지
        QMessageBox.information(self, '선택 완료', f'{time_text} 주차권이 선택되었습니다.')
        
        # 입력 필드 초기화하여 다음 차량 검색 준비
        self.reset_search()
    
    def on_parking_failed(self, error_message):
        self.status_label.setText('주차권 선택 실패')
        self.btn_30min.setEnabled(True)
        self.btn_1hour.setEnabled(True)
        self.btn_1hour30min.setEnabled(True)
        QMessageBox.critical(self, '선택 실패', error_message)
    
    def clear_tickets(self):
        if not self.existing_tickets:
            QMessageBox.information(self, '알림', '제거할 이용권이 없습니다.')
            return
        
        reply = QMessageBox.question(self, '이용권 초기화', '선택된 모든 이용권을 제거하시겠습니까?',
                                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            self.status_label.setText('이용권 초기화 중...')
            self.reset_button.setEnabled(False)
            self.btn_30min.setEnabled(False)
            self.btn_1hour.setEnabled(False)
            self.btn_1hour30min.setEnabled(False)
            
            # 주차권 초기화 스레드 시작
            self.clear_thread = ClearTicketsThread(self.driver)
            self.clear_thread.success.connect(self.on_clear_success)
            self.clear_thread.failed.connect(self.on_clear_failed)
            self.clear_thread.start()
    
    def on_clear_success(self):
        self.status_label.setText('이용권 초기화 완료!')
        self.reset_button.setEnabled(True)
        
        # 초기화 완료 메시지
        QMessageBox.information(self, '초기화 완료', '모든 이용권이 제거되었습니다. 새로운 차량을 검색하세요.')
        
        # 결과 초기화
        self.reset_search()
    
    def on_clear_failed(self, error_message):
        self.status_label.setText('이용권 초기화 실패')
        self.reset_button.setEnabled(True)
        
        # 재시도 여부 확인
        reply = QMessageBox.question(self, '초기화 실패', 
                                    f"{error_message}\n\n다시 시도하시겠습니까?",
                                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            # 다시 시도
            self.clear_tickets()
        else:
            # 버튼 상태 복원
            if self.existing_tickets:
                self.btn_30min.setEnabled(False)
                self.btn_1hour.setEnabled(False)
                self.btn_1hour30min.setEnabled(False)
            else:
                self.btn_30min.setEnabled(True)
                self.btn_1hour.setEnabled(True)
                self.btn_1hour30min.setEnabled(True)
    
    def reset_search(self):
        # 웹페이지 초기화 (크롬창에서 초기화 버튼 클릭)
        try:
            # 초기화 버튼 클릭
            reset_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, '.btn-reset'))
            )
            reset_button.click()
            
            # UI 초기화
            self.car_number_input.clear()
            self.car_info_label.setText('차량 정보: ')
            self.car_image_label.setText('차량 이미지')
            self.existing_tickets_label.setText('기존 이용권: 없음')
            self.selected_time_label.setText('선택된 시간: ')
            self.status_label.setText('')
            
            # 주차권 버튼 비활성화
            self.btn_30min.setEnabled(False)
            self.btn_1hour.setEnabled(False)
            self.btn_1hour30min.setEnabled(False)
            
            # 검색 버튼 활성화 및 포커스 설정
            self.car_number_input.setFocus()  # 차량번호 입력 필드에 포커스 설정
        
        except Exception as e:
            QMessageBox.critical(self, '초기화 오류', f'페이지 초기화 중 오류가 발생했습니다: {str(e)}')
    
    def on_search_timeout(self):
        self.search_attempts += 1
        
        if self.search_attempts < self.max_search_attempts:
            self.status_label.setText(f'검색 시간 초과, 재시도 중... ({self.search_attempts}/{self.max_search_attempts})')
            car_number = self.car_number_input.text().strip()
            self.start_search_thread(car_number)
        else:
            self.status_label.setText('검색 시간 초과, 최대 시도 횟수 초과')
            # 주차권 버튼 비활성화
            self.btn_30min.setEnabled(False)
            self.btn_1hour.setEnabled(False)
            self.btn_1hour30min.setEnabled(False)
            QMessageBox.critical(self, '검색 실패', '검색 시간이 초과되었습니다. 다시 시도해주세요.')
    
    def closeEvent(self, event):
        # 창이 닫힐 때 드라이버 종료
        if self.driver:
            self.driver.quit()
        event.accept()

if __name__ == '__main__':
    # 테스트용 코드 (일반적으로는 login.py에서 실행됨)
    app = QApplication(sys.argv)
    
    # 크롬 드라이버 설정
    options = webdriver.ChromeOptions()
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
    
    window = SearchWindow(driver)
    window.show()
    sys.exit(app.exec()) 