---
name: grill-with-docs
description: grill-me의 도메인 강화판. 심문 과정에서 CONTEXT.md 용어집과 docs/adr/를 그 자리에서 갱신한다(파일 쓰기 발생). "그릴 도큐", "도메인 심문", "용어 정리하면서 캐물어줘", "유비쿼터스 언어", "ADR 남기면서 설계하자", "grill with docs"처럼 문서 갱신까지 명시 요청할 때만. 문서를 건드리지 않는 순수 심문은 grill-me.
metadata:
  invocation: user-invoked
---

> **호출 계층: user-invoked** — 사용자가 직접 호출했거나 명시적으로 요청했을 때만 실행한다. 다른 user-invoked 스킬/커맨드를 호출하지 않는다.

# Grill with Docs

## 심문 코어 — 절차 참조

**`~/.claude/skills/grill-me/SKILL.md`의 프로세스(출발점 파악 → 한 번에 하나의 질문 →
추천 답 동반 → 코드베이스 자체 탐색 → 스펙 산출)를 읽고 그대로 수행한다.**
심문 절차를 여기에 복제하지 않는다 — 원본이 바뀌면 갈라진다.

이 스킬이 **추가**하는 것은 두 가지뿐이다: 심문 중 (1) CONTEXT.md 용어집 대조·갱신,
(2) ADR 판단·기록.

> Kotlin/Spring(Hexagonal), TypeScript/React 작업이면 `~/.claude/architecture-guides/`의
> 해당 가이드를 먼저 읽고, 레이어·경계 관련 추천 답을 가이드 기준으로 잡는다.

## 도메인 인식

코드베이스 탐색 중, 기존 문서도 함께 찾는다.

### 파일 구조

대부분의 repo는 단일 컨텍스트를 가진다:

```
/
├── CONTEXT.md
├── docs/
│   └── adr/
│       ├── 0001-event-sourced-orders.md
│       └── 0002-postgres-for-write-model.md
└── src/
```

루트에 `CONTEXT-MAP.md`가 있으면 여러 컨텍스트를 가진 repo다. 맵은 각 컨텍스트의 위치를 가리킨다:

```
/
├── CONTEXT-MAP.md
├── docs/
│   └── adr/                          ← 시스템 전역 결정
├── src/
│   ├── ordering/
│   │   ├── CONTEXT.md
│   │   └── docs/adr/                 ← 컨텍스트별 결정
│   └── billing/
│       ├── CONTEXT.md
│       └── docs/adr/
```

파일은 **게으르게(lazily)** 만든다 — 쓸 내용이 생겼을 때만. `CONTEXT.md`가 없으면 첫 용어가 해소될 때 만들고, `docs/adr/`가 없으면 첫 ADR이 필요할 때 만든다.

## 세션 중에

### 용어집과 대조해 도전한다

사용자가 `CONTEXT.md`의 기존 언어와 충돌하는 용어를 쓰면 즉시 지적한다. "용어집엔 '취소'가 X로 정의돼 있는데, 지금은 Y를 뜻하는 것 같습니다 — 어느 쪽인가요?"

### 모호한 언어를 날카롭게

사용자가 모호하거나 과적재된 용어를 쓰면, 정확한 표준 용어를 제안한다. "'계정'이라고 하셨는데 — Customer를 말하나요, User를 말하나요? 둘은 다릅니다."

### 구체적 시나리오로 논의

도메인 관계를 논할 땐 구체 시나리오로 압박 테스트한다. 엣지 케이스를 찌르는 시나리오를 만들어 개념 간 경계를 정밀하게 말하도록 강제한다.

### 코드와 교차 검증

사용자가 동작 방식을 말하면 코드가 동의하는지 확인한다. 모순을 발견하면 드러낸다: "코드는 Order 전체를 취소하는데, 방금 부분 취소가 가능하다고 하셨습니다 — 어느 게 맞나요?"

### CONTEXT.md를 인라인으로 갱신

용어가 해소되면 바로 그 자리에서 `CONTEXT.md`를 갱신한다. 모아뒀다 처리하지 말고 발생 즉시 기록한다. 형식은 [references/CONTEXT-FORMAT.md](references/CONTEXT-FORMAT.md) 참조.

`CONTEXT.md`는 구현 디테일이 전혀 없어야 한다. 스펙·스크래치패드·구현 결정 저장소로 다루지 않는다. 그것은 **용어집(glossary)일 뿐이다.**

### ADR은 아껴서 제안한다

다음 세 가지가 모두 참일 때만 ADR 생성을 제안한다:

1. **되돌리기 어렵다** — 나중에 마음을 바꾸는 비용이 의미 있게 크다
2. **맥락 없이는 놀랍다** — 미래의 독자가 "왜 이렇게 했지?"라고 의아해할 것이다
3. **진짜 트레이드오프의 결과다** — 실제 대안이 있었고 특정 이유로 하나를 골랐다

셋 중 하나라도 빠지면 ADR을 건너뛴다. 형식은 [references/ADR-FORMAT.md](references/ADR-FORMAT.md) 참조.
