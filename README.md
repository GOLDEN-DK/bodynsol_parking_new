# 바디앤솔 주차 관리 시스템

바디앤솔 필라테스 회원들의 주차권 발급 및 관리를 위한 시스템입니다.

## 기능

- 차량번호 검색
- 주차권 발급 (30분, 1시간, 1시간 30분)
- 기존 주차권 확인
- 주차권 초기화

## 설치 방법

1. 저장소 클론

```bash
git clone https://github.com/GOLDEN-DK/bodynsol_parking_new.git
cd bodynsol_parking_new
```

2. 가상환경 생성 및 활성화

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. 필요한 패키지 설치

```bash
pip install -r requirements.txt
```

4. ChromeDriver 업데이트

```bash
python update_chromedriver.py
```

## 사용 방법

1. 프로그램 실행

```bash
python main.py
```

2. 로그인 화면에서 아이디와 비밀번호 입력

3. 차량번호 검색 화면에서 차량번호 뒤 4자리 입력 후 검색

4. 검색 결과에서 주차권 선택 (30분, 1시간, 1시간 30분)

5. 주차권 발급 완료 후 다음 차량 검색 가능

6. 이용권 초기화 버튼으로 선택된 주차권 제거 가능

7. 다시 검색 버튼으로 새로운 차량 검색 가능

## 주의사항

- Chrome 브라우저가 설치되어 있어야 합니다.
- 인터넷 연결이 필요합니다.
- 주차 관리 시스템 로그인 정보가 필요합니다.

## 개발 환경

- Python 3.12
- PyQt6
- Selenium
- macOS / Windows 지원
