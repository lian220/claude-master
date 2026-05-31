#!/usr/bin/env bash
# PreToolUse(Bash) 가드레일 — 파괴적 명령을 차단하는 방어선(defense-in-depth).
# permissions.deny 와 별개로, 권한 프롬프트가 생략되는 bypass 모드에서도 작동한다.
# stdin 으로 들어오는 hook JSON 에서 명령을 추출해 위험 패턴을 검사.
# 위험: exit 2 (차단, stderr 가 Claude 에게 피드백됨) / 안전: exit 0.
# JSON 파싱 실패 시 fail-open(exit 0) — 가드레일은 백스톱이므로 워크플로우를 막지 않는다.

input=$(cat)
cmd=$(printf '%s' "$input" | python3 -c 'import sys,json
try:
    print(json.load(sys.stdin).get("tool_input",{}).get("command",""))
except Exception:
    pass' 2>/dev/null)

[ -z "$cmd" ] && exit 0

block() {
  echo "⛔ 가드레일 차단: $1" >&2
  echo "차단된 명령: $cmd" >&2
  echo "(정말 필요하면 사용자에게 확인 후 직접 실행하세요. ~/.claude/hooks/guardrail-bash.sh)" >&2
  exit 2
}

# 루트/홈 강제 삭제
echo "$cmd" | grep -Eq 'rm[[:space:]]+-[a-z]*[rf][a-z]*[[:space:]]+(-[a-z]+[[:space:]]+)*(/|~|\$HOME|/\*)([[:space:]]|/|$)' \
  && block "루트/홈 디렉토리 강제 삭제 (rm -rf /, ~, \$HOME)"

# 루트 권한 일괄 변경
echo "$cmd" | grep -Eq 'chmod[[:space:]]+-R[[:space:]]+0?777[[:space:]]+/([[:space:]]|$)' \
  && block "루트 전체 권한 변경 (chmod -R 777 /)"

# 디스크 직접 쓰기 / 포맷
echo "$cmd" | grep -Eq '(^|[[:space:]])mkfs([[:space:]]|\.)|[[:space:]]of=/dev/(disk|sd|rdisk|nvme|hd)' \
  && block "디스크 직접 쓰기/포맷 (mkfs, dd of=/dev/...)"

# 포크 밤 (BSD grep 호환: 괄호/중괄호/파이프는 bracket class 로 매칭)
echo "$cmd" | grep -Eq '[(][)][[:space:]]*[{][[:space:]]*:[[:space:]]*[|]' \
  && block "포크 밤 (:(){ :|:& };:)"

# 원격 스크립트 파이프 실행
echo "$cmd" | grep -Eq '(curl|wget)[^|]*\|[[:space:]]*(sudo[[:space:]]+)?(ba|z)?sh([[:space:]]|$)' \
  && block "원격 스크립트 파이프 실행 (curl ... | sh)"

# main/master 강제 푸시
echo "$cmd" | grep -Eq 'git[[:space:]]+push[[:space:]].*(--force|--force-with-lease|-f)([[:space:]]).*(main|master)([[:space:]]|:|$)' \
  && block "보호 브랜치(main/master) 강제 푸시"

exit 0
