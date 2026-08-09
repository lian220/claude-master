---
description: Jira 티켓 기반 3단계 개발 사이클 (설계 → TDD → 검증+PR)
argument-hint: "<JIRA-KEY>  예: LAD-42"
---

# 개발 사이클 (3단계 워크플로우)

**사용법**: `/dev-cycle LAD-42`

Jira 티켓 기반 3단계 개발 사이클을 실행합니다.
각 단계 완료 후 사용자 확인을 받고 다음 단계로 진행합니다.

## 인자
- 첫 번째: Jira 티켓 ID (필수, 예: LAD-42)

## 실행 내용

$ARGUMENTS

---

## 1단계: 준비 + 설계

### 1-1. Jira 티켓 시작

**절차 원본**: `~/.claude/commands/jira/start.md` 의 **단계 0 ~ 단계 2**

그 파일을 읽고 거기 적힌 절차를 그대로 수행한다. 브랜치 생성 규칙(MANDATORY),
main/develop pull, 티켓 상태 전환 조건이 모두 그 파일에 있다.

> ⚠️ **이 절차를 여기에 복제하지 말 것.** 복제하면 원본이 바뀔 때 갈라져서
> `/jira:start`로 딴 브랜치와 `/dev-cycle`로 딴 브랜치의 이름 규칙이 달라진다.
> 원본 파일을 읽는 것은 참조이므로 규약상 허용된다. `/jira:start` 커맨드를
> 대신 실행하는 것은 금지된다 (user-invoked 끼리 호출 불가).

수행 후 추가로: **AC(수락 조건) 추출** → 이후 단계에서 검증 기준으로 사용

### 1-2. 아키텍처 설계 (@backend-architect)
1. AC 기반으로 Hexagonal Architecture 설계:
   - **변경 범위 파악**: domain → application → infrastructure → presentation
   - **새로 추가/수정할 파일 목록** 도출
   - **의존성 방향 검증**: Presentation → Application → Domain ← Infrastructure
2. 설계 결과물:
   - 레이어별 변경 파일 목록
   - 새로 만들 Port/Adapter/Entity/VO 정리
   - 테스트 전략 (어떤 레이어부터 테스트할지)

### 1단계 완료 출력
```
📋 1단계 완료: 준비 + 설계

🎫 티켓: {티켓ID} - {제목}
🌿 브랜치: feature/{브랜치명}
📝 AC: {수락 조건 목록}

🏗️ 설계 결과:
- Domain: {변경할 entity/vo/port/service}
- Application: {변경할 usecase}
- Infrastructure: {변경할 adapter/repository}
- Presentation: {변경할 controller/dto}

🧪 테스트 전략: {레이어별 테스트 순서}
```

**→ 사용자에게 확인 요청**: "1단계 설계 결과를 확인해주세요. 2단계(TDD 구현)로 진행할까요?"

---

## 2단계: TDD 구현

1단계 설계를 기반으로 Red→Green→Refactor 사이클을 반복합니다.

### 2-1. 구현 순서 (Hexagonal Architecture)
설계에서 정한 순서대로 진행. 기본 순서:

1. **Domain Layer** (entity, VO, port interface, domain service)
2. **Application Layer** (use case)
3. **Infrastructure Layer** (JPA entity, mapper, repository adapter, 외부 API adapter)
4. **Presentation Layer** (controller, request/response DTO, mapper)

### 2-2. 레이어별 TDD 사이클
각 레이어마다 아래를 반복:

#### Red: 실패하는 테스트 작성
- 테스트 위치 규칙:
  - Domain Service → `test/.../domain/{도메인}/service/`
  - UseCase → `test/.../application/{도메인}/`
  - Controller → `test/.../presentation/rest/`
  - Repository → `test/.../infrastructure/persistence/`
- Given-When-Then 패턴 사용
- 테스트 실행하여 **실패 확인**: `./gradlew test --tests "TestClass"`

#### Green: 테스트 통과하는 최소 코드 작성
- 테스트를 통과시키는 **최소한의 코드**만 작성
- 과도한 설계나 미래 대비 코드 금지 (YAGNI)
- 테스트 실행하여 **통과 확인**

#### Refactor: 코드 구조 개선
- 테스트 통과를 유지하며 중복 제거, 네이밍 개선
- `./gradlew test`로 전체 테스트 통과 확인

### 2-3. 중간 커밋
- 의미 있는 단위로 커밋 (레이어 완성, 주요 기능 완성 등)
- Conventional Commits: `feat({scope}): {메시지} [{티켓ID}]`

### 2단계 완료 출력
```
🔨 2단계 완료: TDD 구현

✅ 구현 완료 파일:
- {파일별 변경 요약}

🧪 테스트 결과:
- 전체: X개 통과 / 0개 실패
- Domain: X개
- Application: X개
- Presentation: X개
- Infrastructure: X개

📝 커밋 이력:
- {커밋 목록}
```

**→ 사용자에게 확인 요청**: "2단계 구현이 완료되었습니다. 3단계(검증 + 완료)로 진행할까요?"

---

## 3단계: 검증 + 완료

### 3-1. 코드 리뷰 (@code-reviewer)
`@code-reviewer` 에이전트를 호출하여 변경사항 리뷰:
- Architecture (Hexagonal 위반 검사)
- Backend (SOLID, exception handling, SQL injection)
- Security (OWASP Top 10)
- General (DRY, dead code, naming)

### 3-2. 이슈 수정 (@debugger)
- 코드 리뷰에서 **Critical/Warning** 이슈가 발견되면:
  - `@debugger` 에이전트로 수정
  - 수정 후 `./gradlew test` 재확인
- 이슈 없으면 이 단계 스킵

### 3-3. 최종 테스트 + Jira 완료 처리

**절차 원본**: `~/.claude/commands/jira/complete.md` 의 **단계 7.5 ~ 단계 9**

그 파일을 읽고 거기 적힌 절차를 그대로 수행한다. 다음이 모두 그 파일에 있다.

- 단계 7.5 — PR 생성 전 필수 테스트 게이트 (실패 시 즉시 중단, PR 생성 금지)
- 단계 8 — 최종 검증 (AC 체크리스트 검토)
- 단계 8.5 — `docs/` 문서 영향 분석·갱신·신규 작성 기준
- 단계 9 — push, PR 생성(제목 `[$1] {티켓 제목}`), Jira 상태 업데이트, PR 링크 연결

> ⚠️ **이 절차를 여기에 복제하지 말 것.** 과거 복제본은 단계 7.5의 테스트 게이트와
> 단계 8.5의 docs 관리 기준을 통째로 누락한 상태였다. 원본 파일을 읽는 것은
> 참조이므로 허용되고, `/jira:complete` 커맨드를 대신 실행하는 것은 금지된다.

### 3단계 완료 출력
```
🎉 3단계 완료: 검증 + 완료

📝 코드 리뷰 결과:
- Critical: 0개
- Warning: 0개
- Suggestion: N개

🧪 최종 테스트: ✅ 전체 통과
🚦 품질 게이트: PASS (Gate 1 ✅ / Gate 2 ✅ / Gate 3 ✅ / Gate 4 ✅)

🔗 PR: {PR URL}
🎫 Jira: {티켓 상태}

✅ 개발 사이클 완료!
```

---

## 중단 및 재개

- 각 단계에서 사용자가 "중단"하면 현재 상태를 커밋하고 중단
- 재개 시 `/dev-cycle $1`을 다시 실행하면 현재 브랜치/상태를 감지하여 적절한 단계부터 재개
- 이미 브랜치가 존재하면 1-1 스킵 → 설계 또는 구현부터 시작

## 핵심 규칙

1. **테스트 없이 비즈니스 로직을 작성하지 않는다**
2. **각 단계 사이에 반드시 사용자 확인을 받는다**
3. **품질 게이트 등급이 `REWORK`/`FAIL`이면 PR을 생성하지 않는다** (`quality-gate` 스킬이 판정. 3-3에서 참조하는 `complete.md` 단계 8에 규칙이 있다)
4. **AC를 모두 충족해야 완료 처리한다**
