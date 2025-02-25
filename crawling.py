import requests
import csv
import time
import random
from datetime import datetime

# 기본 API URL (실제 주소로 변경 필요)
BASE_URL = "https://bff.doctornow.co.kr/graphql/getNewestQuestionCardCursorPage"
DETAIL_URL = "https://bff.doctornow.co.kr/graphql/getQuestionDetail"  # 상세 API 엔드포인트

# 헤더 설정 (필요에 따라 변경)
HEADERS = {"Content-Type": "application/json"}

# 현재 시간 기반 파일명 생성 (YYYYMMDDHHMMSS)
timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
CSV_FILE = f"dataset/dataset_{timestamp}.csv"
CSV_HEADERS = ["questionPid", "title", "title_content", "reply_content"]

# CSV 파일 초기화 (헤더 추가)
with open(CSV_FILE, mode="w", newline="", encoding="utf-8") as file:
    writer = csv.DictWriter(file, fieldnames=CSV_HEADERS)
    writer.writeheader()

# 초기 pivot 값 (최초 요청 시 필요)
pivot = "null"
error_count = 0  # 연속 오류 횟수

while True:
    try:
        # API 요청을 위한 payload 구성
        base_payload = {"operationName": "getNewestQuestionCardCursorPage",
                    "query": "\n    query getNewestQuestionCardCursorPage($request: NewestQuestionCardCursorPageRequestInput!) {\n  newestQuestionCardCursorPage(request: $request) {\n    elements {\n      answer {\n        answerPid\n        answerer {\n          affiliatedInstitutionName\n          answererId\n          answererType\n          name\n          professionalFields {\n            name\n            professionalFieldId\n            professionalFieldType\n          }\n          profileImageUrl\n        }\n        content\n        createdAt\n        dislikeCount\n        footer\n        header\n        isBlockedByUser\n        likeCount\n        myLikeType\n      }\n      answeredStatus\n      answererCount\n      answererProfileImageUrls\n      question {\n        status\n        accessibleType\n        attachments {\n          blindType\n          questionAttachmentId\n        }\n        category {\n          name\n          questionCategoryId\n          iconImageUrl\n        }\n        content\n        createdAt\n        isBlockedByMe\n        isLikedByMe\n        isMine\n        likeCount\n        questionPid\n        tags {\n          name\n        }\n        title\n        user {\n          name\n          userId\n        }\n      }\n    }\n    pivot\n  }\n}\n    ",
                    "variables": {"request": {"size": 100, "answered": "false", "categoryId": "2", "pivot": pivot}}
                    } if pivot else {}

        # 메인 API 요청
        response = requests.post(BASE_URL, json=base_payload, headers=HEADERS)

        if response.status_code == 200:
            data = response.json()

            # elements 가져오기
            elements = data.get("data", {}).get("newestQuestionCardCursorPage", {}).get("elements", [])
            pivot = data.get("data", {}).get("newestQuestionCardCursorPage", {}).get("pivot")  # 다음 요청을 위한 pivot 갱신

            if not elements:
                print("더 이상 데이터가 없습니다. 종료합니다.")
                break

            with open(CSV_FILE, mode="a", newline="", encoding="utf-8") as file:
                writer = csv.DictWriter(file, fieldnames=CSV_HEADERS)

                for item in elements:
                    question = item.get("question", {})
                    question_pid = question.get("questionPid")
                    title = question.get("title", "제목 없음")
                    title_content = question.get("content", "내용 없음")
                    reply_content = "답변 없음"

                    datail_payload = {"operationName": "getQuestionDetail",
                                    "query": "\n    query getQuestionDetail($questionPid: ID!, $size: Int) {\n  question(questionPid: $questionPid) {\n    accessibleType\n    paymentInfo {\n      discountAmount\n      paidAmount\n      paidAt\n      payTryCount\n      price\n      usedPoint\n    }\n    paymentTotal {\n      currentAmount\n      payTrackingNumber\n      reason\n      status\n      userPaymentId\n      userPayment {\n        cardName\n        cardNumber\n        id\n      }\n    }\n    status\n    answererCount\n    answeredStatus\n    answers {\n      answerPid\n      answerer {\n        affiliatedInstitutionName\n        answererId\n        answererPublicId\n        answererType\n        name\n        profileImageUrl\n        affiliation {\n          address\n          affiliationPid\n          imageUrl\n          name\n        }\n      }\n      content\n      createdAt\n      dislikeCount\n      footer\n      header\n      isBlockedByMe\n      likeCount\n      myLikeType\n      reviews {\n        id\n        answerPid\n        rating\n        content\n        createdAt\n        updatedAt\n        reviewTags {\n          id\n          text\n        }\n      }\n      recommendedMagazineGraph {\n        description\n        magazinePid\n        title\n        titleImageUrl\n      }\n    }\n    attachments {\n      blindType\n      questionAttachmentId\n    }\n    category {\n      name\n      questionCategoryId\n      type\n    }\n    content\n    createdAt\n    isBlockedByMe\n    isLikedByMe\n    isMine\n    likeCount\n    questionPid\n    showUserPersonalInfo\n    tags {\n      name\n    }\n    title\n    user {\n      name\n      userId\n      birth\n      gender\n    }\n  }\n  nearSimpleQuestions(request: {questionPid: $questionPid, size: $size}) {\n    questionPid\n  }\n}\n    ",
                                    "variables": {"questionPid": question_pid, "size": 1}
                                    } if pivot else {}

                    # 랜덤한 딜레이 추가 (1~3초)
                    delay = random.uniform(1, 3)
                    time.sleep(delay)

                    # 상세 API 요청 (questionPid 사용)
                    detail_response = requests.post(DETAIL_URL, json=datail_payload, headers=HEADERS)
                    if detail_response.status_code == 200:
                        detail_data = detail_response.json()
                        answers = detail_data.get("data", {}).get("question", {}).get("answers", [])
                        reply_content = answers[0].get("content", "답변 없음")

                    # CSV 저장
                    writer.writerow({
                        "questionPid": question_pid,
                        "title": title,
                        "title_content": title_content,
                        "reply_content": reply_content,
                    })

                    print(f"저장 완료: {question_pid} | {title}")

            error_count = 0  # 성공했으므로 오류 횟수 초기화

        else:
            print(f"요청 실패: {response.status_code}, 응답 내용: {response.text}")
            error_count += 1

    except Exception as e:
        print(f"요청 중 오류 발생: {e}")
        error_count += 1

    # 연속 오류가 5번 발생하면 종료
    if error_count >= 5:
        print("연속 5회 요청 실패. 종료합니다.")
        break

