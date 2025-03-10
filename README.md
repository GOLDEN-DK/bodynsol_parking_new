# 주차 관리 시스템

이 프로젝트는 PyQt6와 Selenium을 사용하여 주차 관리 웹사이트에 접속하여 차량 검색 및 주차권 발급을 자동화하는 시스템입니다.

## 기능

- 웹사이트 자동 로그인
- 차량번호 검색
- 차량 이미지 확인
- 주차권 시간 선택 (30분, 1시간, 1시간 30분)
- 주차권 발급 자동화

## 설치 방법

1. 필요한 패키지 설치:

```
pip install -r requirements.txt
```

2. Chrome 브라우저가 설치되어 있어야 합니다.

## 사용 방법

1. 프로그램 실행:

```
python main.py
```

2. 로그인 화면에서 아이디와 비밀번호를 입력하고 로그인 버튼을 클릭합니다.

   - 기본값으로 아이디와 비밀번호가 설정되어 있습니다.

3. 차량 검색 화면에서 차량번호 뒤 4자리를 입력하고 검색 버튼을 클릭합니다.

4. 차량 이미지와 정보를 확인한 후, 원하는 주차 시간을 선택합니다.

   - 30분, 1시간, 1시간 30분 중 선택 가능합니다.

5. 주차권 발급이 완료되면 알림이 표시되고, 다음 차량 검색을 위해 화면이 초기화됩니다.

## 프로젝트 구조

- `main.py`: 메인 실행 파일
- `login.py`: 로그인 기능 구현
- `search.py`: 차량 검색 및 주차권 발급 기능 구현
- `requirements.txt`: 필요한 패키지 목록

## 주의사항

- 인터넷 연결이 필요합니다.
- Chrome 브라우저가 설치되어 있어야 합니다.
- 웹사이트의 구조가 변경될 경우 프로그램이 정상 작동하지 않을 수 있습니다.
