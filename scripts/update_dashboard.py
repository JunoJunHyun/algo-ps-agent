import json
from collections import Counter
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
STATS_PATH = BASE_DIR / "data" / "stats.json"
README_PATH = BASE_DIR / "README.md"

def build_readme():
    stats = json.loads(STATS_PATH.read_text(encoding="utf-8")) if STATS_PATH.exists() else []
    today = datetime.now().strftime("%Y-%m-%d")

    total = len(stats)
    lang_counts = Counter(s.get("language", "C++") for s in stats)
    cat_counts = Counter(s["category"] for s in stats)

    pending_reviews = [s for s in stats if s.get("review_status") == "pending"]
    pending_reviews.sort(key=lambda x: x.get("review_due") or "9999-99-99")

    weak_scores = Counter()
    for s in stats:
        score = (2 if s.get("assisted") else 0) + len(s.get("weak_points", []))
        weak_scores[f"{s.get('language', 'C++')}-{s['category']}"] += score
    top_weak = weak_scores.most_common(2)

    lang_summary = " · ".join(f"`{k}` {v}" for k, v in lang_counts.most_common()) or "없음"
    cat_summary = " · ".join(f"`{k}` {v}" for k, v in cat_counts.most_common()) or "아직 풀이 기록 없음"
    weak_summary = ", ".join(f"**{k}** ({v}pt)" for k, v in top_weak) or "데이터 수집 중"

    review_lines = []
    for r in pending_reviews:
        due = r["review_due"]
        urgent = "🚨 **오늘 복습!**" if due <= today else f"📅 {due} 예정"
        review_lines.append(f"- {urgent} | [{r['title']}]({r['url']}) (`{r.get('language', 'C++')}` / `{r['category']}`) — 통과 후 `python run.py {r['problem_id']} --review-done`")
    review_block = "\n".join(review_lines) if review_lines else "- 🎉 현재 밀린 복습 대기가 없습니다."

    table_rows = []
    for s in reversed(stats):
        status = s.get("review_status")
        if status == "pending":
            re_col = f"🔴 대기 ({s['review_due'][5:]})"
        elif status == "done":
            re_col = f"🟢 완료 ({(s.get('review_done_date') or '')[5:]})"
        else:
            re_col = "⚪ 자력"

        clean_comment = s["comment"].replace("|", "/")
        row = (
            f"| {s.get('language', 'C++')} | {s['category']} | {s['level']} | [{s['title']}]({s['url']}) | "
            f"[리뷰](./{s['md_path']}) | {clean_comment} | {s['solved_date']} | {re_col} |"
        )
        table_rows.append(row)

    table_block = "\n".join(table_rows) if table_rows else "| - | - | - | 첫 문제를 등록해 주세요 | - | - | - | - |"

    readme = f"""# 🧠 Algo-PS-Agent (코딩테스트 & SQL 오차 분석 · 복습 자동화)

굿노트(iPad) 손필기 설계와 실제 구현 코드(C++, Java, Python, C, SQL) 사이의 **문법·쿼리·예외 처리 괴리(Gap)**를 AI로 분석하고, **3일 망각곡선 기반 백지 재풀이**를 강제하는 학습 파이프라인입니다.

---

## 📊 학습 현황 & AI 취약점 진단

- **총 해결 문제:** `{total}문제` ({lang_summary})
- **유형별 분포:** {cat_summary}
- **현재 취약 영역 TOP 2:** {weak_summary}
- **마지막 동기화:** `{today}`

### ⏰ 3일 주기 백지 재풀이 알리미
{review_block}

---

## 📝 문제 풀이 아카이브

| 언어 | 유형 | 난이도 | 문제 | 상세 리뷰 | 핵심 한 줄 요약 (Comment) | 푼 날짜 | 복습 상태 |
| :---: | :--- | :---: | :--- | :---: | :--- | :---: | :---: |
{table_block}

---

## ⚙️ 시스템 아키텍처 (Why & How)

1. **문제 해결 배경:** 코테 입문 단계에서 손코딩 반복의 비효율을 줄이고, 설계 단계에서 놓친 언어별 문법·쿼리 예외 실수를 데이터로 누적하기 위해 구축했습니다.
2. **파이프라인 흐름:** `GoodNotes 설계(PDF)` + `통과 코드` → `Gemini Custom Skill (Structured JSON)` → `Markdown 리뷰 & stats.json 생성` → `GitHub Actions 대시보드 자동 갱신`
3. **학습 검증 루프:** 강의를 참고한 문제는 자동으로 `🔴 복습 대기(D+3)` 상태로 분류되며, 3일 뒤 백지 상태에서 재풀이 통과 후 `--review-done` 플래그로 검증을 마쳐야 `🟢 완료`로 전환됩니다.
"""
    README_PATH.write_text(readme, encoding="utf-8")
    print("📊 README.md 대시보드가 최신 상태로 갱신되었습니다.")

if __name__ == "__main__":
    build_readme()
