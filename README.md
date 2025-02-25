# dataset

- 닥터나우 실시간 의료상담 > 내과 크롤링
    - 분야 변경 시 base_payload의 categoryId값 수정
- JSON 결과를 csv로 저장(timestamp로 구분)
    - ["질문 PID", "질문 제목", "질문 내용", "답변 내용"]
- 봇 의심을 피하기 위해 각 요청 당 1~3초 랜덤 delay 적용