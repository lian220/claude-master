---
description: "프로젝트별 기술 스택/아키텍처 결정을 기록하고 잠금. 코딩 패턴은 글로벌 가이드(~/.claude/architecture-guides/) 참조."
---

# Architecture Lock

프로젝트별 기술 스택과 아키텍처 결정을 잠금 파일로 기록합니다.
코딩 패턴(UseCase 구조, 컴포넌트 설계 등)은 글로벌 가이드를 따릅니다.

## 역할 분리

- **글로벌 가이드** (`~/.claude/architecture-guides/`) — 언어별 코딩 패턴 (HOW to write code)
- **프로젝트 잠금** (`architecture-decisions.md`) — 프로젝트별 기술 선택 (WHAT to use)

## 절차

1. 프로젝트의 기존 코드, CLAUDE.md, 플랜 문서를 분석하여 기술 스택과 아키텍처 결정을 추출한다.
2. 사용자에게 추출한 결정 목록을 보여주고 확인/수정을 받는다.
3. 확인된 내용으로 프로젝트 루트에 `architecture-decisions.md`를 생성한다.

## architecture-decisions.md 형식

```markdown
# Architecture Decisions (LOCKED)

> 이 파일이 존재하는 동안 아래 결정에 반하는 대안을 검색하거나 제안하지 않습니다.
> 변경이 필요하면 사용자와 논의 후 이 파일을 업데이트하세요.

## Tech Stack
- Language: [e.g., Kotlin, TypeScript]
- Framework: [e.g., Spring Boot 4.x, Next.js 16]
- Database: [e.g., PostgreSQL + pgvector]

## Architecture Pattern
- [e.g., Hexagonal Architecture]
- [e.g., Feature-scoped Frontend]

## Key Decisions
| 영역 | 결정 | 근거 |
|------|------|------|
| ORM | Exposed 1.0 | Kotlin 네이티브 |
| Data Fetching | TanStack Query v5 | 캐싱, 옵티미스틱 업데이트 |
| 메시징 | Redis Streams | 팀 규모 적정 |

## Applied Guides
- ~/.claude/architecture-guides/kotlin.md
- ~/.claude/architecture-guides/react.md

## Locked Date
[날짜]
```

4. 생성 완료 후 `🔒 아키텍처 잠금 완료` 메시지를 출력한다.
