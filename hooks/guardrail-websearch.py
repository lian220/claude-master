#!/usr/bin/env python3
"""PreToolUse(WebSearch|WebFetch) 가드레일 — 아키텍처 가이드 우선 규칙을 주입한다.

~/.claude/architecture-guides/ 에 언어별 코딩 가이드가 있으면, 웹에서 대안 패턴을
찾아 가이드를 우회하는 것을 막기 위해 검색 직전에 규칙을 상기시킨다.

규칙은 반드시 JSON hookSpecificOutput.additionalContext 로 내보낸다.
PreToolUse 의 stdout 평문은 디버그 로그로만 가고 모델에게 전달되지 않는다
(컨텍스트가 되는 이벤트는 UserPromptSubmit / UserPromptExpansion / SessionStart 뿐).
이전 버전은 평문 echo 였기 때문에 규칙이 실제로는 한 번도 주입되지 않았다.

차단하지 않는다. 공식 문서·API 레퍼런스·에러 해결 검색은 정상 작업이다.
가이드 디렉토리가 없거나 비어 있으면 아무것도 하지 않는다(fail-open).
"""

import json
import os
import sys

GUIDE_DIR = os.path.join(os.path.expanduser("~"), ".claude", "architecture-guides")

# 검색어에서 특정 언어가 감지되면 해당 가이드를 지목한다.
ALIASES = {
    "kotlin": ["kotlin", "kt", "spring", "gradle", "jpa", "ktlint"],
    "python": ["python", "py", "django", "fastapi", "pytest"],
    "typescript": ["typescript", "ts", "tsx", "javascript", "js", "node"],
    "react": ["react", "jsx", "next.js", "nextjs", "hook", "component"],
}


def emit(context):
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


def guides():
    try:
        return sorted(
            f for f in os.listdir(GUIDE_DIR) if f.endswith(".md")
        )
    except Exception:
        return []


def haystack(payload):
    """WebSearch 는 query, WebFetch 는 url + prompt 를 갖는다."""
    ti = payload.get("tool_input") or {}
    parts = [ti.get("query"), ti.get("url"), ti.get("prompt")]
    return " ".join(p for p in parts if isinstance(p, str)).lower()


def relevant(text, available):
    hits = []
    for stem, words in ALIASES.items():
        name = stem + ".md"
        if name in available and any(w in text for w in words):
            hits.append(name)
    return hits


def main():
    available = guides()
    if not available:
        return  # 가이드 없음 — 규칙도 없다

    try:
        payload = json.load(sys.stdin)
    except Exception:
        payload = {}

    hits = relevant(haystack(payload), available)

    lines = [
        "⛔ ARCHITECTURE GUIDES LOCKED",
        "",
        f"코딩 아키텍처 가이드가 있다: {GUIDE_DIR}",
        "- 허용: 채택된 기술의 공식 문서, API 레퍼런스, 에러 해결, 버전/릴리스 확인",
        "- 금지: 가이드에 반하는 대안 패턴·코딩 스타일 검색 및 제안",
        "- 가이드 변경이 필요해 보이면 직접 바꾸지 말고 사용자에게 먼저 확인한다",
        "",
    ]

    if hits:
        lines.append("이 검색과 관련된 가이드 — 검색 결과를 적용하기 전에 먼저 읽을 것:")
        lines += [f"  - {os.path.join(GUIDE_DIR, h)}" for h in hits]
    else:
        lines.append("가이드 목록: " + ", ".join(available))

    emit("\n".join(lines))


if __name__ == "__main__":
    main()
