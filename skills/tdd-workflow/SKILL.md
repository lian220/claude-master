---
name: tdd-workflow
description: 백엔드에 검증 가능한 로직(UseCase, 도메인 서비스, API 엔드포인트, 비즈니스 규칙)을 새로 만들 때 적용하는 TDD 규율. Red→Green→Refactor 순서를 강제하고 테스트 없는 비즈니스 로직 작성을 금지한다. 설정 변경·문서 작성·단순 리팩터링·UI 마크업에는 적용하지 않는다. superpowers:test-driven-development 가 활성인 환경에서는 TDD 사이클 강제를 그쪽에 맡기고, 이 스킬은 Hexagonal 레이어별 테스트 배치 규칙만 제공한다.
metadata:
  invocation: model-invoked
---

> **호출 계층: model-invoked** — 작업 성격에 맞으면 모델이 스스로 적용하는 재사용 규율. user-invoked 스킬/커맨드를 호출하지 않는다.

# TDD 규율

검증 가능한 로직을 새로 만들 때 지키는 규칙. 오케스트레이션(설계→구현→검증 단계 진행)은
이 스킬의 일이 아니다 — 그건 `/dev-cycle`이 한다.

## Red → Green → Refactor

- **Red**: 실패하는 테스트를 먼저 작성하고, **실패하는 이유를 확인**한다.
  늘 통과하는 테스트는 아무것도 검사하지 않는다.
- **Green**: 그 테스트를 통과시키는 **최소한의 코드**만 작성한다.
  "나중에 쓸 것 같아서" 미리 만들지 않는다 (YAGNI).
- **Refactor**: 테스트 통과를 유지한 채 중복 제거·네이밍 개선. 구조만 다듬는다.
- 한 번에 하나의 테스트만 추가하고 사이클을 반복한다.

## 핵심 규칙

1. 테스트 없이 비즈니스 로직을 작성하지 않는다
2. 테스트보다 먼저 작성된 구현 코드는 버린다
3. 구현 후 전체 테스트 통과를 확인한다 (빌드 도구는 프로젝트에서 감지:
   `build.gradle.kts` → `./gradlew test`, `package.json` → `npm test`)

## 상세 가이드

- **테스트 작성 패턴**: [references/test-patterns.md](references/test-patterns.md)
- **Hexagonal 레이어별 테스트 배치**: [references/hexagonal-testing.md](references/hexagonal-testing.md)
- Kotlin 프로젝트는 `~/.claude/architecture-guides/kotlin.md` §6(Fake > Mock, 네이밍)이 상위 규범이다.
