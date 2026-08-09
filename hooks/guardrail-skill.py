#!/usr/bin/env python3
"""PreToolUse(Skill) 가드레일 — user-invoked 스킬의 자동 발동을 경고한다.

원리: 사용자가 /커맨드를 직접 타이핑하면 스킬이 곧바로 로드되어 Skill 툴을 거치지 않는다.
      모델이 스스로 꺼낼 때만 Skill 툴을 호출한다.
      따라서 이 훅이 발동했다 = 모델의 자체 판단으로 발동시켰다는 뜻이다.
      (주의: Claude Code 버전에 따라 이 전제가 흔들린 이력이 있다. docs 참조)

차단하지 않는다. 사용자가 자연어로 "그릴 좀 해줘"라고 명시 요청한 경우도 Skill 툴을
타기 때문에, 차단하면 오탐이 된다. 판단은 모델에게 남기고 근거만 제공한다.

경고는 반드시 JSON hookSpecificOutput.additionalContext 로 내보낸다.
PreToolUse 의 stdout 은 디버그 로그로만 가고 모델에게 전달되지 않기 때문이다
(공식 문서상 stdout 이 컨텍스트가 되는 이벤트는 UserPromptSubmit /
UserPromptExpansion / SessionStart 뿐이다). 평문 echo 로는 아무 효과가 없다.

판단 근거: 스킬은 SKILL.md 의 metadata.invocation 필드.
          커맨드는 정의상 user-invoked (프론트매터로 model-invoked opt-out 가능).
대상 파일을 못 찾으면 fail-open. 플러그인 스킬(superpowers: 등)은 규약 대상이 아니다.

규약 전문: docs/skill-invocation-tiers.md
"""

import json
import os
import re
import sys

TIERS = {"user-invoked", "model-invoked"}


def emit(context):
    """모델이 실제로 읽는 유일한 경로. stdout 평문은 전달되지 않는다."""
    json.dump(
        {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "additionalContext": context,
            }
        },
        sys.stdout,
        ensure_ascii=False,
    )


def candidate_paths(skill):
    """프로젝트 로컬 스코프를 유저 스코프보다 먼저 본다."""
    nested = skill.replace(":", "/")
    bases = []
    project = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
    bases.append((os.path.join(project, ".claude"), "project"))
    bases.append((os.environ.get("CLAUDE_CONFIG_DIR") or
                  os.path.expanduser("~/.claude"), "user"))
    for base, _ in bases:
        yield "skill", os.path.join(base, "skills", skill, "SKILL.md")
        yield "command", os.path.join(base, "commands", skill + ".md")
        yield "command", os.path.join(base, "commands", nested + ".md")


def read_frontmatter(text):
    """YAML 프론트매터 블록만 잘라낸다. 없으면 None."""
    m = re.match(r"^---[ \t]*\n(.*?)\n---[ \t]*(?:\n|$)", text, re.DOTALL)
    return m.group(1) if m else None


def strip_value(raw):
    """인라인 주석과 따옴표를 제거한다."""
    raw = re.sub(r"\s+#.*$", "", raw).strip()
    if len(raw) >= 2 and raw[0] == raw[-1] and raw[0] in "\"'":
        raw = raw[1:-1]
    return raw.strip().lower()


def parse_tier(front):
    """metadata.invocation 만 정확히 읽는다.

    awk 부분매칭이 auto-invocation / 주석줄 / description 본문의 문자열까지
    집어삼키던 오탐·미탐을 막기 위해 블록 구조를 직접 따라간다.
    """
    tier = None
    hard_blocked = False
    misplaced = False
    meta_indent = None

    for line in front.split("\n"):
        if not line.strip() or line.lstrip().startswith("#"):
            continue

        indent = len(line) - len(line.lstrip())
        m = re.match(r"^([A-Za-z0-9_-]+)[ \t]*:(.*)$", line.strip())
        if not m:
            # 블록 스칼라 본문 등 — 키가 아니면 무시한다.
            continue
        key, rest = m.group(1), m.group(2)

        if indent == 0:
            if key == "metadata":
                meta_indent = 0
                continue
            meta_indent = None
            if key == "disable-model-invocation" and strip_value(rest) == "true":
                hard_blocked = True
            elif key == "invocation":
                # metadata 밖 선언. 검증기는 거부하지만 훅이 침묵하면
                # 잘못 선언된 user-invoked 가 조용히 발동한다.
                misplaced = True
            continue

        if meta_indent is not None and key == "invocation":
            tier = strip_value(rest)

    return tier, hard_blocked, misplaced


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return
    skill = (payload.get("tool_input") or {}).get("skill") or ""
    if not skill:
        return

    kind = target = None
    for k, path in candidate_paths(skill):
        if os.path.isfile(path):
            kind, target = k, path
            break
    if not target:
        return  # 플러그인/외부 스킬 — 규약 대상 아님

    try:
        front = read_frontmatter(open(target, encoding="utf-8").read())
    except Exception:
        return
    if front is None:
        return

    tier, hard_blocked, misplaced = parse_tier(front)

    if misplaced and tier is None:
        emit(
            f"⚠️ [{skill}] 는 invocation 을 metadata 밖에 선언했습니다 ({target}).\n"
            "올바른 위치는 metadata.invocation 이며, 현재 상태는 검증기(quick_validate.py)도"
            " 거부합니다.\n"
            "계층 판정이 불가능하므로 실행 전 사용자에게 알리고 수정하세요."
        )
        return

    # 오타를 조용히 넘기면 규약이 소리 없이 무너진다.
    if tier is not None and tier not in TIERS:
        emit(
            f"⚠️ [{skill}] 의 metadata.invocation 값이 잘못되었습니다: {tier!r}\n"
            f"허용값: user-invoked / model-invoked ({target})\n"
            "규약 위반이므로 사용자에게 알리고 수정하세요."
        )
        return

    if tier is None and kind == "command":
        tier = "user-invoked"  # 커맨드는 정의상 user-invoked
    if hard_blocked:
        tier = "user-invoked"

    if tier != "user-invoked":
        return

    label = "커맨드" if kind == "command" else "스킬"
    emit(
        f"⚠️ [{skill}] 는 user-invoked {label}입니다.\n"
        f"사용자가 /{skill} 를 직접 입력했거나 명시적으로 요청한 경우에만 진행하세요.\n"
        "그렇지 않다면 지금 실행하지 말고, 무엇을 하려는지 먼저 사용자에게 확인받으세요.\n"
        "오케스트레이터(user-invoked)끼리는 서로 호출할 수 없습니다.\n"
        "(규약: docs/skill-invocation-tiers.md)"
    )


if __name__ == "__main__":
    main()
