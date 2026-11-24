import subprocess
import sys

def run_cmd(cmd):
    res = subprocess.run(cmd)
    if res.returncode != 0:
        sys.exit(res.returncode)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("사용법: python run.py <문제번호> [--assisted | --review-done]")
        sys.exit(1)

    problem_id = sys.argv[1]
    extra_flags = sys.argv[2:]

    run_cmd([sys.executable, "scripts/agent.py", problem_id, *extra_flags])
    run_cmd([sys.executable, "scripts/update_dashboard.py"])

    subprocess.run(["git", "add", "."], check=True)
    msg = f"review: {problem_id} 복습 완료" if "--review-done" in extra_flags else f"solve: {problem_id} 풀이 및 오차 분석"
    subprocess.run(["git", "commit", "-m", msg], check=False)

    remotes = subprocess.check_output(["git", "remote"]).decode().strip()
    if remotes:
        subprocess.run(["git", "push", "origin", "main"], check=True)
        print("🚀 GitHub 자동 Push 완료!")
    else:
        print("ℹ️ 아직 GitHub 원격 저장소(origin)가 연결되지 않아 로컬 저장만 완료했습니다.")
