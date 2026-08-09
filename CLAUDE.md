# Global Rules

## Communication Rules

- **스킬 호출 알림**: Skill tool로 스킬을 호출할 때 반드시 `⚡ [스킬명] 실행` 형태로 한 줄 알림을 먼저 출력한다 (예: `⚡ tdd-workflow 실행`). 사용자가 직접 입력한 `/커맨드`는 제외.
- **에이전트 실행 알림**: Agent tool로 서브에이전트를 실행할 때 반드시 `🤖 [에이전트타입]: [설명]` 형태로 한 줄 알림을 먼저 출력한다 (예: `🤖 Explore: 프로젝트 구조 탐색`, `🤖 code-reviewer: 코드 리뷰 실행`).

## Architecture Guide Rules

- `~/.claude/architecture-guides/`에 언어별 코딩 아키텍처 가이드가 존재한다 (kotlin.md, python.md, typescript.md, react.md).
- 코드 작성 시 해당 언어의 가이드를 **먼저 읽고 따른다**.
- 가이드에 반하는 대안 패턴/코딩 스타일을 웹검색하거나 제안하지 않는다.
- 서브에이전트에게 코드 작업을 위임할 때 해당 언어의 가이드를 명시한다:
  - Kotlin → `~/.claude/architecture-guides/kotlin.md`
  - Python → `~/.claude/architecture-guides/python.md`
  - TypeScript → `~/.claude/architecture-guides/typescript.md`
  - React → `~/.claude/architecture-guides/react.md`
- 가이드 변경이 필요하다고 판단되면 **직접 변경하지 말고 사용자에게 먼저 확인**한다.
