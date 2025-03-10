언어는 python
GUI : PyQt6
크롬 드라이버 사용

단계마다 별도 파일을 생성해서, 쉽게 수정할 수 있게 구성함.

- 로그인 단계
- 검색화면 및 검색단계
- 차량확인 및 주차권 입력 단계
- 주차권정보확인 단계
  초기화 단계

Selenium: 특정 사이트(크롬 브라우저 기반) 로그인-차량 조회-주차시간 등록
SQLite: 요청 로그, 세션, 회원정보 등 간단한 로컬 데이터베이스 관리
Windows: 최종 실행 환경(.exe로 빌드 가능)

사용자 GUI 프로그램 실행
크롬브라우저 로그인

차량번호 4자리와 주차시간 선택 후 ‘확인’ 클릭
   Selenium으로 사이트 로그인(필요 시) 및 차량 검색
   첫 번째 검색 결과 사진 URL 확보 -> GUI에 표시
   사용자가 확인 버튼을 누르면 주차시간 등록 버튼 자동 클릭
   DB에 요청 이력과 결과를 기록 -> 완료 후 사용자에게 성공/실패 메시지

접속 웹사이트 : http://kmp0000673.iptime.org/cooperators/home
아이디 : 바디앤솔
비밀번호 : 2728

아이디
//\*[@id="form-login-username"]

비밀번호
//\*[@id="form-login-password"]

로그인 버튼
//\*[@id="form-login"]/div[3]/button

차량번호 입력
//\*[@id="visit-lpn"]

//\*[@id="visit-lpn"]

차량번호 조회 버튼
//\*[@id="btn-find"]
//\*[@id="visit-lpn"]

초기화 버튼
//\*[@id="btn-init"]
//\*[@id="btn-init"]

해당 xpath에 차량 번호가 11부1111 형태로 나오면, 차량 조회 성공이야.
끝에 4자리가 일치
//\*[@id="page-view"]/table/tbody/tr[1]/td[2]

차량 이미지를 나타내는 xpath.
//\*[@id="page-view"]/table/tbody/tr[8]/td/img

1시간 버튼 xpath - 클릭하면 반영됨.
//\*[@id="page-view"]/table/tbody/tr[5]/td/button

30분 버튼 xpath - 클릭하면 반영됨.
//\*[@id="page-view"]/table/tbody/tr[7]/td/button

선택하면 아래에

<td class="gbox-body-cell">
                            <div class="qbox-filter-field">
                                1시간(유료)
                                
                                / 바디앤솔 필라테스
                                &nbsp;<button type="button" class="btn btn-inline btn-cancel-visit-coupon" data-id="V2025022617291769559">X</button>
                            </div>
                            <div class="qbox-filter-field">
                                30분(유료)
                                
                                / 바디앤솔 필라테스
                                &nbsp;<button type="button" class="btn btn-inline btn-cancel-visit-coupon" data-id="V2025022617291983720">X</button>
                            </div>
</td>

이렇게 표시됨.

확인 좀 해줘.
차량번호는 이미지에서 번호를 추출하는 것이 아니라,
해당 차량 이미지 xpath에 이미지가 들어가 있는지만 확인 하면 돼.

그리고 검색화면은 내가 수동으로 돌아가게 한거야.

다음 시간 선택은 사용자가 이미지를 확인하고 나서
30분, 1시간, 1시간 30분 단위로 버튼을 선택해서

웹페이지에 해당 하는 시간 버튼을 클릭하면 되는거야.
웹페이지 시간버튼은 1시간버튼과 30분 버튼이 있어.
따라서 1시간 30분은 1시간 버튼 하나, 30분 버튼 하나를 클릭하면 돼.

그리고 선택을 하면, 선택한 것을 표시를 해주는 소스야 확인 해줘.
이 부분 확인 한 후 선택되었습니다. 라는 알림창과 함께 다음 차량을 입력할 수 있게 해주면 돼.
