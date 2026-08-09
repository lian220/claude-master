---
name: quality-gate
description: 4단계 품질 게이트 시스템. 빌드·테스트/코드품질/보안/아키텍처를 판정해 PASS·CONCERNS·REWORK·FAIL 등급을 매기고, REWORK 이상이면 PR 생성을 차단한다. "품질 검증", "quality check", "배포 전 확인", "PR 준비" 키워드에 반응. /jira:complete 단계 8에서 적용되며 /dev-cycle 은 이를 절차 참조로 물려받는다. 이미 실행된 테스트·리뷰 결과를 재사용하고 재실행하지 않는다.
metadata:
  invocation: model-invoked
---

> **호출 계층: model-invoked** — 작업 성격에 맞으면 모델이 스스로 적용하는 재사용 규율. user-invoked 스킬/커맨드를 호출하지 않는다.

# Quality Gate System

## 4단계 등급

| 등급 | 의미 | 조건 | 행동 |
|------|------|------|------|
| **PASS** | 배포 가능 | 모든 게이트 통과 | PR 생성 진행 |
| **CONCERNS** | 조건부 통과 | Minor 이슈만 존재 | 이슈 목록 표시, 판단은 사용자에게 |
| **REWORK** | 재작업 필요 | Major 이슈 존재 | 수정 후 재검증 필수 |
| **FAIL** | 차단 | Critical 이슈 존재 | PR 생성 차단, 즉시 수정 |

## 게이트 체크리스트

### Gate 1: 빌드 & 테스트

**앞선 단계(jira:complete 7.5 등)의 테스트 결과가 있으면 그것을 쓴다. 아래 명령은
결과가 없을 때만 실행하는 fallback이다** (재실행 금지 — 하단 표 참조).

```bash
# 빌드 도구는 프로젝트에서 감지한다 (build.gradle.kts → gradle / package.json → npm)
# Backend 예시
./gradlew clean build test --no-daemon

# Frontend 예시 (변경 시)
npm run lint && npm run build
```
- [ ] 빌드 성공
- [ ] 전체 테스트 통과
- [ ] 린트 에러 없음

### Gate 2: 코드 품질
- [ ] 새 코드에 테스트 존재 (비즈니스 로직)
- [ ] Hexagonal Architecture 위반 없음
- [ ] DRY 위반 없음 (중복 코드)
- [ ] 네이밍 컨벤션 준수
- [ ] 불필요한 TODO/FIXME 없음

### Gate 3: 보안
- [ ] 하드코딩된 시크릿 없음
- [ ] SQL injection 가능성 없음
- [ ] 입력 유효성 검증 있음
- [ ] 민감 정보 로그 출력 없음
- [ ] CORS 설정 적절

### Gate 4: 아키텍처
- [ ] Domain → Infrastructure 의존 없음
- [ ] Controller에 비즈니스 로직 없음
- [ ] DTO와 Domain Entity 분리
- [ ] Port/Adapter 패턴 준수
- [ ] 트랜잭션 경계 올바름

## 등급 산정 로직

```
Gate 결과 수집:
├── Gate 1 실패 → FAIL (빌드/테스트 실패는 무조건 차단)
├── Gate 2-4 중 Critical → FAIL
├── Gate 2-4 중 Major → REWORK
├── Gate 2-4 중 Minor만 → CONCERNS
└── 모두 통과 → PASS
```

## 출력 형식

```
## Quality Gate Report

### 등급: [PASS | CONCERNS | REWORK | FAIL]

📦 Gate 1 - Build & Test: ✅/❌
  - Backend: X tests passed
  - Frontend: lint ✅, build ✅

📝 Gate 2 - Code Quality: ✅/⚠️/❌
  - [항목별 결과]

🛡️ Gate 3 - Security: ✅/⚠️/❌
  - [항목별 결과]

🏗️ Gate 4 - Architecture: ✅/⚠️/❌
  - [항목별 결과]

### 결론
[등급에 따른 다음 행동 안내]
```

## 호출자

이 스킬은 model-invoked 재사용 규율이다. **스스로 발동하지 않고 오케스트레이터가 끌어다 쓴다.**

- `/jira:complete` **단계 8**에서 적용된다. 등급이 `REWORK`/`FAIL`이면 PR 생성이 차단된다.
- `/dev-cycle` 3단계는 `complete.md` 단계 7.5~9를 절차 참조하므로 위 판정을 그대로 물려받는다.
  별도로 한 번 더 판정하지 않는다.

## 재실행 금지

**이 스킬은 판정자이지 재실행자가 아니다.** 이미 실행된 검사를 다시 돌리지 않는다.

| Gate | 결과를 어디서 가져오나 |
|------|----------------------|
| Gate 1 (빌드·테스트) | `jira:complete` 단계 7.5의 테스트 결과 |
| Gate 2~4 (품질·보안·아키텍처) | 앞서 실행한 `@code-reviewer` / `@security-sentinel` 결과 |

해당 결과가 없을 때만 직접 검사한다. 있는데도 다시 돌리면 `./gradlew test`가 두 번 실행된다.
