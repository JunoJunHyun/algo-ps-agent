# 🧠 Algo-PS-Agent (코딩테스트 & SQL 오차 분석 · 복습 자동화)

굿노트(iPad) 손필기 설계와 실제 구현 코드(C++, Java, Python, C, SQL) 사이의 **문법·쿼리·예외 처리 괴리**를 AI로 분석하고, **3일 망각곡선 기반 백지 재풀이**를 강제하는 학습 파이프라인입니다.

---

## 📊 학습 현황 & AI 취약점 진단

- **총 해결 문제:** `3문제` (`Python` 2 · `C++` 1)
- **유형별 분포:** `String` 2 · `Brute_Force` 1
- **현재 취약 영역 TOP 2:** **C++-String** (5pt), **Python-String** (4pt)
- **마지막 동기화:** `2026-11-26`

### ⏰ 3일 주기 백지 재풀이 알리미
- 📅 2026-11-27 예정 | [신규아이디추천](https://school.programmers.co.kr/learn/courses/30/lessons/72410) (`C++` / `String`) — 통과 후 `python run.py 72410 --review-done`
- 📅 2026-11-29 예정 | [중요한단어를스포방지](https://school.programmers.co.kr/learn/courses/30/lessons/468370) (`Python` / `String`) — 통과 후 `python run.py 468370 --review-done`

---

## 📝 문제 풀이 아카이브

| 언어 | 유형 | 난이도 | 문제 | 상세 리뷰 | 핵심 한 줄 요약 (Comment) | 푼 날짜 | 복습 상태 |
| :---: | :--- | :---: | :--- | :---: | :--- | :---: | :---: |
| Python | String | Lv.1 | [중요한단어를스포방지](https://school.programmers.co.kr/learn/courses/30/lessons/468370) | [리뷰](./solutions/String/중요한단어를스포방지_468370_python.md) | 구간 인덱스 매핑 및 공개순 판별 | 2026-11-26 | 🔴 대기 (11-29) |
| Python | Brute_Force | Lv.1 | [노란불신호등](https://school.programmers.co.kr/learn/courses/30/lessons/468371) | [리뷰](./solutions/Brute_Force/노란불신호등_468371_python.md) | 주기 최소공배수 범위 완전탐색 | 2026-11-25 | ⚪ 자력 |
| C++ | String | Lv.1 | [신규아이디추천](https://school.programmers.co.kr/learn/courses/30/lessons/72410) | [리뷰](./solutions/String/신규아이디추천_72410_cpp.md) | 정규표현식 활용 7단계 문자열 처리 | 2026-11-24 | 🔴 대기 (11-27) |

---

## ⚙️ 시스템 아키텍처 (Why & How)

1. **문제 해결 배경:** 코테 입문 단계에서 손코딩 반복의 비효율을 줄이고, 설계 단계에서 놓친 언어별 문법·쿼리 예외 실수를 데이터로 누적하기 위해 구축했습니다.
2. **파이프라인 흐름:** `GoodNotes 설계(PDF)` + `통과 코드` → `Gemini Custom Skill (Structured JSON)` → `Markdown 리뷰 & stats.json 생성` → `GitHub Actions 대시보드 자동 갱신`
3. **학습 검증 루프:** 강의를 참고한 문제는 자동으로 `🔴 복습 대기(D+3)` 상태로 분류되며, 3일 뒤 백지 상태에서 재풀이 통과 후 `--review-done` 플래그로 검증을 마쳐야 `🟢 완료`로 전환됩니다.
