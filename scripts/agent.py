import argparse
import json
import re
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import List
from pydantic import BaseModel, Field

BASE_DIR = Path(__file__).resolve().parent.parent

LANG_TAG = {
    "C++": "cpp",
    "Java": "java",
    "Python": "python",
    "C": "c",
    "SQL": "sql",
}

class ReviewResult(BaseModel):
    problem_title: str
    problem_url: str
    language: str
    category: str
    level: str
    one_line_comment: str
    design_summary: List[str]
    gap_analysis: List[str]
    failure_analysis: List[str] = Field(default_factory=list)
    lang_tips: List[str]
    code: str = ""
    fail_code: str = ""

def get_clipboard_json() -> str:
    raw = subprocess.check_output(["pbpaste"]).decode("utf-8").strip()
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)
    return raw.strip()

def mark_review_done(problem_id: str):
    stats_path = BASE_DIR / "data" / "stats.json"
    if not stats_path.exists():
        print("❌ 기록된 stats.json 데이터가 없습니다.")
        return

    stats = json.loads(stats_path.read_text(encoding="utf-8"))
    today = datetime.now().strftime("%Y-%m-%d")
    updated = False

    for item in stats:
        if item["problem_id"] == problem_id and item.get("review_status") == "pending":
            item["review_status"] = "done"
            item["review_done_date"] = today
            md_file = BASE_DIR / item["md_path"]
            if md_file.exists():
                text = md_file.read_text(encoding="utf-8")
                text = text.replace("🔴 복습 대기", f"🟢 재풀이 완료 ({today} 백지 통과)")
                md_file.write_text(text, encoding="utf-8")
            updated = True
            print(f"🟢 [{item['title']} ({item.get('language', 'C++')})] 백지 재풀이 완료!")

    if not updated:
        print(f"❌ 문제 번호 {problem_id}의 복습 대기 기록을 찾을 수 없습니다.")
        return

    stats_path.write_text(json.dumps(stats, ensure_ascii=False, indent=2), encoding="utf-8")

def save_from_clipboard(problem_id: str, assisted: bool):
    try:
        raw_json = get_clipboard_json()
        result = ReviewResult.model_validate_json(raw_json)
    except Exception as e:
        print(f"❌ 클립보드 JSON 읽기 실패: 채팅에서 JSON 블록을 먼저 복사해 주세요.\n상세: {e}")
        return

    code_text = result.code.strip()
    fail_text = result.fail_code.strip()
    if not code_text:
        print("❌ 통과 코드(code)가 비어 있습니다.")
        return

    lang = result.language.strip()
    tag = LANG_TAG.get(lang, lang.lower())
    base_folder = "sql" if lang.upper() == "SQL" else "solutions"

    today = datetime.now().strftime("%Y-%m-%d")
    review_due = (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d") if assisted else None

    out_dir = BASE_DIR / base_folder / result.category
    out_dir.mkdir(parents=True, exist_ok=True)
    md_rel_path = f"{base_folder}/{result.category}/{result.problem_title}_{problem_id}_{tag}.md"
    md_path = BASE_DIR / md_rel_path

    re_badge = f"🔴 복습 대기 ({review_due} 예정)" if assisted else "⚪ 자력 완료"
    design_md = "\n".join(f"- {x}" for x in result.design_summary)
    gap_md = "\n".join(f"- {x}" for x in result.gap_analysis)
    tips_md = "\n".join(f"- {x}" for x in result.lang_tips)

    bt = "`" * 3
    fail_md = ""
    if fail_text and result.failure_analysis:
        reasons = "\n".join(f"- {x}" for x in result.failure_analysis)
        fail_md = f"\n## 3. 실패 과정 & 원인 분석\n{reasons}\n\n{bt}{tag}\n{fail_text}\n{bt}\n"

    md_content = f"""# [{lang}] {result.problem_title} ({result.level})

- **문제 링크:** [{problem_id}번 바로가기]({result.problem_url})
- **언어 / 유형:** {lang} / {result.category}
- **푼 날짜:** {today}
- **복습 상태:** {re_badge}
- **핵심 요약:** {result.one_line_comment}

## 1. 굿노트 설계 요약
{design_md}

## 2. 필기 vs 실제 코드 오차 분석 (Gap Analysis)
{gap_md}
{fail_md}
## {'4' if fail_md else '3'}. {lang} 실전 개선 팁
{tips_md}

## {'5' if fail_md else '4'}. 최종 통과 코드 ({lang})
{bt}{tag}
{code_text}
{bt}
"""
    md_path.write_text(md_content, encoding="utf-8")

    stats_path = BASE_DIR / "data" / "stats.json"
    stats = json.loads(stats_path.read_text(encoding="utf-8")) if stats_path.exists() else []
    stats = [s for s in stats if not (s["problem_id"] == problem_id and s.get("language") == lang)]
    stats.append({
        "problem_id": problem_id,
        "title": result.problem_title,
        "url": result.problem_url,
        "language": lang,
        "category": result.category,
        "level": result.level,
        "comment": result.one_line_comment,
        "md_path": md_rel_path,
        "solved_date": today,
        "assisted": assisted,
        "review_status": "pending" if assisted else "self_solved",
        "review_due": review_due,
        "review_done_date": None,
        "weak_points": result.gap_analysis,
    })
    stats_path.write_text(json.dumps(stats, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"✅ [{lang}] 회고록 생성 완료: {md_rel_path}")
    if review_due:
        print(f"⏰ 3일 뒤({review_due}) 백지 재풀이 알림이 대시보드에 등록되었습니다.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("problem_id", help="문제 번호 (예: 72410)")
    parser.add_argument("--assisted", action="store_true", help="강의/풀이 참고 시 부여")
    parser.add_argument("--review-done", action="store_true", help="3일 뒤 백지 재풀이 통과 시 부여")
    args = parser.parse_args()

    if args.review_done:
        mark_review_done(args.problem_id)
    else:
        save_from_clipboard(args.problem_id, args.assisted)
