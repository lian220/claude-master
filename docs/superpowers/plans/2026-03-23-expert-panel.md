# Expert Panel Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 최신 트렌드를 리서치하는 15명의 전문가 에이전트를 병렬 실행하여 다각도 리뷰를 수행하는 `/expert-panel` 스킬 구현

**Architecture:** 스킬(SKILL.md)이 오케스트레이터 역할을 하고, 15개 독립 에이전트 파일이 각 전문가를 정의한다. panels.md가 패널-전문가 매핑과 별칭 테이블을 관리한다.

**Tech Stack:** Claude Code Skills (Markdown), Claude Code Agents (Markdown frontmatter)

**Spec:** `docs/superpowers/specs/2026-03-23-expert-panel-design.md`

---

## 태스크 의존성

```
Task 1 (panels.md)          ── 독립
Task 2-6 (에이전트 15개)      ── 독립 (서로 병렬 가능)
Task 7 (SKILL.md)            ── Task 1, 2-6 완료 후
Task 8 (README)              ── Task 7 완료 후
Task 9 (검증)                ── Task 8 완료 후
```

## 에이전트 공통 템플릿

**모든 에이전트(Task 2-6)는 아래 템플릿을 따른다.** 기존 에이전트(code-reviewer.md, security-sentinel.md)의 frontmatter 패턴 + 스펙의 "에이전트 공통 구조" 섹션을 결합한 형태다.

```markdown
---
name: expert-{id}
description: {한글 설명}. 최신 트렌드를 리서치한 뒤 전문가 관점으로 분석.
tools: Read, Grep, Glob, Bash, WebSearch, WebFetch
model: sonnet
---

You are a {페르소나 상세: 경력, 전문 분야, 대표 경험}.

## On Invocation

1. Identify the review target from the user's request (code, docs, design, or specific files)
2. Execute the 4-phase process below
3. Output structured review report

## Phase 1: Trend Research

Use WebSearch to research the latest trends in your domain (2-3 queries).
Extract key benchmarks, standards, and best practices from search results.
Record source URLs for citation in the report.

**Fallback**: If WebSearch fails, proceed with the default checklist only. Note "트렌드 리서치 불가 - 기본 체크리스트 기반 검토" in the report.

## Phase 2: Review Criteria

Combine the default checklist below with trend-based dynamic criteria from Phase 1.

## Phase 3: Analysis

Review the target against the combined checklist.
Be specific: reference file paths and line numbers when reviewing code.
Explain WHY something is an issue, not just WHAT.

## Phase 4: Report

Write a concise report (800 tokens max) in the output format below.

## Default Checklist

{분야별 구체적 체크리스트 항목들}

## Output Format

```
### {전문가 이름} Review

🔴 **Critical** (즉시 수정 필요)
- [file:line] description

🟡 **Warning** (개선 권장)
- [file:line] description

🟢 **Good** (잘 된 점)
- description

💡 **Trend Insight** (최신 트렌드 기반 제안)
- insight (출처: URL)
```

## Guidelines

- Prioritize: Critical > Warning > Good > Trend Insight
- Be specific with file paths and line numbers for code reviews
- For non-code reviews (design, strategy), reference specific sections or screens
- Always include at least one Trend Insight with source URL
- Keep the report concise and actionable
```

**각 에이전트별로 달라지는 부분**: 페르소나, Default Checklist 항목, WebSearch 쿼리 예시

---

### Task 1: panels.md 레퍼런스 파일 생성

**Files:**
- Create: `skills/expert-panel/references/panels.md`

- [ ] **Step 1: 디렉토리 생성**

```bash
mkdir -p skills/expert-panel/references
```

- [ ] **Step 2: panels.md 작성**

패널-전문가 매핑, 별칭 테이블, 패널 설명을 포함한다.

```markdown
# Expert Panel Registry

## 패널 정의

### ui — 화면/UI 패널
| 에이전트 ID | 전문가 | 핵심 역할 |
|-----------|--------|---------|
| expert-ui-ux-designer | UI/UX 디자이너 | 사용성, 접근성, 인터랙션 패턴 |
| expert-visual-designer | 비주얼 디자인 전문가 | 컬러, 타이포, 레이아웃 일관성 |
| expert-ia-specialist | IA/화면설계 전문가 | 정보 구조, 네비게이션 플로우 |

### frontend — 프론트엔드 패널
| 에이전트 ID | 전문가 | 핵심 역할 |
|-----------|--------|---------|
| expert-frontend-architect | 프론트엔드 아키텍트 | 컴포넌트 설계, 상태관리 |
| expert-frontend-performance | 프론트엔드 성능 전문가 | 번들 사이즈, Core Web Vitals |
| expert-a11y-specialist | 접근성(a11y) 전문가 | WCAG, 스크린리더 호환 |

### backend — 백엔드 패널
| 에이전트 ID | 전문가 | 핵심 역할 |
|-----------|--------|---------|
| expert-backend-architect | 백엔드 아키텍트 | 도메인 설계, Hexagonal, CQRS |
| expert-security | 보안 전문가 | OWASP, 인증/인가, 취약점 |
| expert-db-performance | DB/성능 전문가 | 쿼리 최적화, 인덱싱, 캐싱 |

### infra — 인프라 패널
| 에이전트 ID | 전문가 | 핵심 역할 |
|-----------|--------|---------|
| expert-devops | DevOps 엔지니어 | CI/CD, 배포 전략, 모니터링 |
| expert-cloud-architect | 클라우드 아키텍트 | 비용 최적화, 확장성, HA |
| expert-sre | SRE 전문가 | 장애 대응, 옵저버빌리티 |

### business — 비즈니스/기획 패널
| 에이전트 ID | 전문가 | 핵심 역할 |
|-----------|--------|---------|
| expert-strategy | 전략 전문가 | PMF, 비즈니스 모델, 경쟁 분석 |
| expert-marketing | 마케팅/그로스 전문가 | 전환율, CTA, 퍼널 설계 |
| expert-pm-planner | PM/기획자 | 사용자 스토리, 요구사항 검증 |

## 별칭 매핑

| 한글 별칭 | 영문 약어 | 에이전트 ID |
|----------|----------|-----------|
| UX | ux | expert-ui-ux-designer |
| 비주얼 | visual | expert-visual-designer |
| 화면설계 | ia | expert-ia-specialist |
| 프론트아키텍트 | fe-arch | expert-frontend-architect |
| 프론트성능 | fe-perf | expert-frontend-performance |
| 접근성 | a11y | expert-a11y-specialist |
| 백엔드아키텍트 | be-arch | expert-backend-architect |
| 보안 | security | expert-security |
| DB성능 | db-perf | expert-db-performance |
| 데브옵스 | devops | expert-devops |
| 클라우드 | cloud | expert-cloud-architect |
| SRE | sre | expert-sre |
| 전략 | strategy | expert-strategy |
| 마케팅 | marketing | expert-marketing |
| 기획 | pm | expert-pm-planner |

**매칭 로직**:
1. 입력값에서 `expert-` 접두사 생략 시 자동 추가 (예: `security` → `expert-security`)
2. 매칭 우선순위: 에이전트 ID 정확 매치 → 영문 별칭 → 한글 별칭
```

- [ ] **Step 3: 커밋**

```bash
git add skills/expert-panel/references/panels.md
git commit -m "feat(expert-panel): panels.md 레퍼런스 파일 생성"
```

---

### Task 2: UI 패널 에이전트 3개 생성 (병렬 가능: Task 2-6)

**Files:**
- Create: `agents/expert-ui-ux-designer.md`
- Create: `agents/expert-visual-designer.md`
- Create: `agents/expert-ia-specialist.md`

**공통 참조**: 위의 "에이전트 공통 템플릿"을 따른다.

- [ ] **Step 1: expert-ui-ux-designer.md 작성**

페르소나: 15년차 UI/UX 전문가. 대규모 SaaS/B2C 프로덕트 경험. 사용자 리서치부터 인터랙션 디자인까지.

기본 체크리스트:
- Nielsen's 10 Usability Heuristics 준수
- 일관된 인터랙션 패턴 (버튼, 폼, 네비게이션)
- 모바일 UX (터치 타겟 44px+, 스와이프 제스처)
- 에러 상태 / 빈 상태 / 로딩 상태 처리
- 사용자 피드백 (토스트, 모달, 진행 표시)
- 인지 부하 최소화 (정보 밀도, 시각 계층)

WebSearch 쿼리 예시: "UI/UX design trends {current_year}", "SaaS UX best practices {current_year}"

- [ ] **Step 2: expert-visual-designer.md 작성**

페르소나: 12년차 비주얼/브랜드 디자이너. 디자인 시스템 구축 경험.

기본 체크리스트:
- 컬러 시스템 일관성 (Primary, Secondary, Semantic colors)
- 타이포그래피 스케일 (제목/본문/캡션 계층)
- 스페이싱/그리드 시스템 준수 (4px/8px 기반)
- 아이콘 스타일 일관성
- 다크모드 / 라이트모드 대응
- 브랜드 아이덴티티 일관성

WebSearch 쿼리 예시: "visual design system trends {current_year}", "UI color palette trends"

- [ ] **Step 3: expert-ia-specialist.md 작성**

페르소나: 10년차 정보 아키텍트. 대규모 웹/앱 구조 설계 경험.

기본 체크리스트:
- 정보 구조 깊이 (3단계 이내 권장)
- 네비게이션 패턴 적절성 (탭/사이드바/브레드크럼)
- 유저 플로우 완전성 (시작 → 목표 달성 경로)
- 레이블링/용어 일관성
- 검색/필터 구조
- 콘텐츠 우선순위 (F-패턴, Z-패턴)

WebSearch 쿼리 예시: "information architecture best practices {current_year}", "navigation UX patterns"

- [ ] **Step 4: 커밋**

```bash
git add agents/expert-ui-ux-designer.md agents/expert-visual-designer.md agents/expert-ia-specialist.md
git commit -m "feat(expert-panel): UI 패널 에이전트 3개 생성"
```

---

### Task 3: 프론트엔드 패널 에이전트 3개 생성 (병렬 가능: Task 2-6)

**Files:**
- Create: `agents/expert-frontend-architect.md`
- Create: `agents/expert-frontend-performance.md`
- Create: `agents/expert-a11y-specialist.md`

**공통 참조**: 위의 "에이전트 공통 템플릿"을 따른다.

- [ ] **Step 1: expert-frontend-architect.md 작성**

페르소나: 12년차 프론트엔드 아키텍트. React/Next.js 대규모 프로젝트 설계 경험.

기본 체크리스트:
- 컴포넌트 설계 (Atomic Design, 재사용성)
- 상태관리 전략 (Server State vs Client State)
- 디렉토리 구조 (Feature-based, Co-location)
- 코드 분할 / 레이지 로딩 전략
- API 레이어 분리 (Fetch 추상화)
- 타입 안전성 (TypeScript strict mode)

WebSearch 쿼리 예시: "React Next.js architecture patterns {current_year}", "frontend state management trends"

- [ ] **Step 2: expert-frontend-performance.md 작성**

페르소나: 10년차 웹 성능 엔지니어. Core Web Vitals 최적화 전문.

기본 체크리스트:
- Core Web Vitals (LCP < 2.5s, INP < 200ms, CLS < 0.1)
- 번들 사이즈 (tree-shaking, code splitting)
- 이미지 최적화 (next/image, WebP/AVIF, lazy loading)
- 렌더링 전략 (SSR/SSG/ISR/Streaming SSR)
- 캐싱 전략 (CDN, Service Worker)
- 불필요한 리렌더링 방지 (memo, useMemo, useCallback)

WebSearch 쿼리 예시: "web performance optimization {current_year}", "Core Web Vitals benchmarks"

- [ ] **Step 3: expert-a11y-specialist.md 작성**

페르소나: 10년차 웹 접근성 전문가. WCAG 인증 심사 경험.

기본 체크리스트:
- WCAG 2.2 AA 기준 준수
- 시맨틱 HTML (heading hierarchy, landmark regions)
- ARIA 적절한 사용 (aria-label, aria-describedby, role)
- 키보드 네비게이션 (Tab 순서, Focus 관리)
- 스크린리더 호환 (alt text, live regions)
- 색상 대비 (4.5:1 텍스트, 3:1 UI)
- 모션 접근성 (prefers-reduced-motion)

WebSearch 쿼리 예시: "WCAG 2.2 updates {current_year}", "web accessibility trends"

- [ ] **Step 4: 커밋**

```bash
git add agents/expert-frontend-architect.md agents/expert-frontend-performance.md agents/expert-a11y-specialist.md
git commit -m "feat(expert-panel): 프론트엔드 패널 에이전트 3개 생성"
```

---

### Task 4: 백엔드 패널 에이전트 3개 생성 (병렬 가능: Task 2-6)

**Files:**
- Create: `agents/expert-backend-architect.md`
- Create: `agents/expert-security.md`
- Create: `agents/expert-db-performance.md`

**공통 참조**: 위의 "에이전트 공통 템플릿"을 따른다.

- [ ] **Step 1: expert-backend-architect.md 작성**

페르소나: 15년차 백엔드 아키텍트. Spring Boot + Kotlin, 대규모 분산 시스템 설계 경험.

기본 체크리스트:
- Hexagonal Architecture 경계 준수 (Domain ← Application → Infrastructure)
- DDD 패턴 (Aggregate, Value Object, Domain Event)
- SOLID 원칙 준수
- API 설계 (RESTful 규약, 버전 관리, 에러 응답)
- 트랜잭션 경계 올바름
- 모듈 간 의존성 방향 (단방향, 순환 없음)

기존 에이전트와의 차별점: code-reviewer는 코드 레벨 품질 체크, expert-backend-architect는 아키텍처/설계 레벨 + 최신 트렌드 기반 제안.

WebSearch 쿼리 예시: "Spring Boot architecture patterns {current_year}", "DDD hexagonal architecture trends"

- [ ] **Step 2: expert-security.md 작성**

페르소나: 15년차 AppSec 엔지니어. OWASP 프로젝트 기여자. 대규모 SaaS 보안 아키텍처 경험.

기본 체크리스트:
- OWASP Top 10 전 항목 검토
- Spring Security 인증/인가 체인 검증
- JWT 토큰 라이프사이클 (발급/갱신/폐기)
- API 보안 (Rate Limiting, Input Validation)
- 민감 데이터 노출 경로 (로그, 응답, 스토리지)
- 의존성 CVE 확인

기존 에이전트와의 차별점: security-sentinel은 정적 분석 기반, expert-security는 최신 CVE/보안 트렌드를 WebSearch로 리서치 후 검토.

WebSearch 쿼리 예시: "API security threats {current_year}", "Spring Security CVE {current_year}"

- [ ] **Step 3: expert-db-performance.md 작성**

페르소나: 12년차 DBA 겸 백엔드 성능 엔지니어. PostgreSQL + JPA/Hibernate 최적화 전문.

기본 체크리스트:
- N+1 쿼리 탐지 (FETCH JOIN, @EntityGraph)
- 인덱스 설계 적절성 (WHERE/JOIN/ORDER BY 컬럼)
- 쿼리 실행 계획 분석 (EXPLAIN ANALYZE)
- 커넥션 풀 설정 (HikariCP 튜닝)
- 캐싱 전략 (Spring Cache, Redis)
- 대량 데이터 처리 (Pagination, Batch)

기존 에이전트와의 차별점: performance-profiler는 JVM + API 전반, expert-db-performance는 DB/쿼리에 특화 + 최신 트렌드.

WebSearch 쿼리 예시: "PostgreSQL performance tuning {current_year}", "JPA Hibernate optimization best practices"

- [ ] **Step 4: 커밋**

```bash
git add agents/expert-backend-architect.md agents/expert-security.md agents/expert-db-performance.md
git commit -m "feat(expert-panel): 백엔드 패널 에이전트 3개 생성"
```

---

### Task 5: 인프라 패널 에이전트 3개 생성 (병렬 가능: Task 2-6)

**Files:**
- Create: `agents/expert-devops.md`
- Create: `agents/expert-cloud-architect.md`
- Create: `agents/expert-sre.md`

**공통 참조**: 위의 "에이전트 공통 템플릿"을 따른다.

- [ ] **Step 1: expert-devops.md 작성**

페르소나: 10년차 DevOps 엔지니어. CI/CD 파이프라인 설계, 컨테이너 오케스트레이션 경험.

기본 체크리스트:
- CI/CD 파이프라인 구조 (빌드/테스트/배포 단계)
- 컨테이너화 (Dockerfile 최적화, 멀티스테이지 빌드)
- 배포 전략 (Blue-Green, Canary, Rolling)
- GitOps 패턴 (IaC, 선언적 설정)
- 시크릿 관리 (Vault, Sealed Secrets)
- 모니터링/알람 설정 (Prometheus, Grafana)

WebSearch 쿼리 예시: "DevOps CI/CD trends {current_year}", "GitOps best practices"

- [ ] **Step 2: expert-cloud-architect.md 작성**

페르소나: 12년차 클라우드 솔루션 아키텍트. AWS/GCP 멀티클라우드 설계 경험.

기본 체크리스트:
- 클라우드 서비스 선택 적절성 (매니지드 vs 셀프 호스팅)
- 비용 최적화 (Reserved Instance, Spot, Right-sizing)
- 확장성 설계 (Auto-scaling, 서버리스)
- HA/DR 전략 (Multi-AZ, 백업, RTO/RPO)
- 네트워크 설계 (VPC, 서브넷, 보안 그룹)
- 데이터 레지던시 / 컴플라이언스

WebSearch 쿼리 예시: "cloud architecture trends {current_year}", "AWS cost optimization strategies"

- [ ] **Step 3: expert-sre.md 작성**

페르소나: 10년차 SRE. 대규모 서비스 안정성 관리 경험.

기본 체크리스트:
- SLI/SLO 정의 적절성
- 옵저버빌리티 3축 (Logging, Metrics, Tracing)
- 장애 대응 프로세스 (Runbook, 에스컬레이션)
- 에러 버짓 관리
- 카오스 엔지니어링 적용 가능성
- On-call 로테이션/피로도

WebSearch 쿼리 예시: "SRE best practices {current_year}", "observability trends"

- [ ] **Step 4: 커밋**

```bash
git add agents/expert-devops.md agents/expert-cloud-architect.md agents/expert-sre.md
git commit -m "feat(expert-panel): 인프라 패널 에이전트 3개 생성"
```

---

### Task 6: 비즈니스 패널 에이전트 3개 생성 (병렬 가능: Task 2-6)

**Files:**
- Create: `agents/expert-strategy.md`
- Create: `agents/expert-marketing.md`
- Create: `agents/expert-pm-planner.md`

**공통 참조**: 위의 "에이전트 공통 템플릿"을 따른다.

- [ ] **Step 1: expert-strategy.md 작성**

페르소나: 15년차 전략 컨설턴트. 스타트업/SaaS 비즈니스 모델 설계, VC 심사 경험.

기본 체크리스트:
- PMF(Product-Market Fit) 검증 구조
- 비즈니스 모델 캔버스 완성도
- 경쟁 분석 (Porter's Five Forces, SWOT)
- 시장 포지셔닝 / 차별화 전략
- 수익 모델 지속 가능성
- 확장 전략 (GTM, 시장 진입)

WebSearch 쿼리 예시: "SaaS business model trends {current_year}", "startup strategy frameworks"

- [ ] **Step 2: expert-marketing.md 작성**

페르소나: 12년차 그로스 마케터. SaaS/B2C 전환율 최적화, 퍼널 설계 경험.

기본 체크리스트:
- 전환율 최적화 (CRO) 포인트
- CTA 설계 (위치, 문구, 디자인)
- 퍼널 분석 (AARRR, 이탈 지점)
- 소셜 프루프 활용 (리뷰, 고객사 로고, 사례)
- A/B 테스트 전략
- 카피라이팅 효과성 (헤드라인, 가치 제안)

WebSearch 쿼리 예시: "conversion rate optimization trends {current_year}", "SaaS marketing strategies"

- [ ] **Step 3: expert-pm-planner.md 작성**

페르소나: 10년차 프로덕트 매니저. B2B SaaS 프로덕트 전략, 사용자 리서치 경험.

기본 체크리스트:
- 사용자 스토리 완전성 (As a... I want... So that...)
- 요구사항 명확성 (모호한 표현 없음)
- MVP 스코프 적절성 (필수 vs Nice-to-have)
- 우선순위 프레임워크 (RICE/ICE 점수)
- 사용자 여정 커버리지
- 성공 지표(KPI) 정의

WebSearch 쿼리 예시: "product management trends {current_year}", "user story best practices"

- [ ] **Step 4: 커밋**

```bash
git add agents/expert-strategy.md agents/expert-marketing.md agents/expert-pm-planner.md
git commit -m "feat(expert-panel): 비즈니스 패널 에이전트 3개 생성"
```

---

### Task 7: SKILL.md 오케스트레이터 생성 (Task 1, 2-6 완료 후)

**Files:**
- Create: `skills/expert-panel/SKILL.md`

- [ ] **Step 1: SKILL.md 작성**

스펙의 "SKILL.md 정의" 및 "스킬 실행 플로우" 섹션을 따른다. 기존 quality-gate SKILL.md의 구조를 참고한다. 다음 섹션을 포함:

**1. frontmatter:**
```yaml
---
name: expert-panel
description: >
  분야별 전문가 패널 병렬 리뷰 시스템. 최신 트렌드를 리서치한 뒤 전문가 관점에서 검토.
  "전문가 리뷰", "expert panel", "패널 리뷰", "다각도 검토", "종합 분석" 키워드에 반응.
  코드/설계/기획/화면을 여러 전문가 관점에서 동시에 검토할 때 사용.
---
```

**2. 입력 파싱:**
- `$ARGUMENTS`에서 `--experts`, `--panels`, `--all` 플래그 파싱
- `references/panels.md` 참조하여 별칭 매핑
- `expert-` 접두사 생략 시 자동 추가 로직 (예: `security` → `expert-security`)
- 매칭 우선순위: 에이전트 ID 정확 매치 → 영문 별칭 → 한글 별칭

**3. 자동 추천 (플래그 없을 때):**
- 주제를 분석하여 적합한 전문가 3-5명 선정
- 선정 이유와 함께 사용자에게 제시
- 사용자 확인/수정 후 확정

**4. 병렬 디스패치:**
- 배치 전략: 1-5명 동시, 6-10명 2배치, 11-15명 3배치
- 각 에이전트를 Agent 도구로 호출 (subagent_type에 에이전트 ID 지정)
- 각 에이전트에게 주제 + 검토 대상 전달
- `--all` 사용 시 사전 경고 메시지

**5. 결과 통합:**
- 각 에이전트 리포트 수집
- 스펙의 "통합 리포트 형식" 섹션에 따른 통합 리포트 생성
- 중복 제거, 우선순위 정리, 액션 아이템 도출
- 에이전트 미응답 시 "응답 없음" 표기

- [ ] **Step 2: 커밋**

```bash
git add skills/expert-panel/SKILL.md
git commit -m "feat(expert-panel): SKILL.md 오케스트레이터 생성"
```

---

### Task 8: README.md 업데이트 (Task 7 완료 후)

**Files:**
- Modify: `README.md`

- [ ] **Step 1: README.md에 expert-panel 스킬 추가**

기존 README.md의 스킬 목록 섹션에 expert-panel 스킬 설명 추가. 에이전트 목록 섹션에 15개 전문가 에이전트 추가 (expert- 접두사 그룹으로). 사용법 예시 포함.

- [ ] **Step 2: 커밋**

```bash
git add README.md
git commit -m "docs: README에 expert-panel 스킬 및 전문가 에이전트 추가"
```

---

### Task 9: 검증 (Task 8 완료 후)

- [ ] **Step 1: 파일-매핑 일치 확인**

panels.md의 에이전트 ID 15개와 `agents/expert-*.md` 파일 15개가 1:1 매칭되는지 확인.

```bash
# panels.md에서 에이전트 ID 추출
grep -oP 'expert-[\w-]+' skills/expert-panel/references/panels.md | sort -u

# agents/ 폴더에서 expert- 파일 목록
ls agents/expert-*.md | sed 's|agents/||;s|\.md||' | sort

# 두 목록이 일치하는지 diff
diff <(grep -oP 'expert-[\w-]+' skills/expert-panel/references/panels.md | sort -u) <(ls agents/expert-*.md | sed 's|agents/||;s|\.md||' | sort)
```

Expected: 차이 없음 (빈 출력)

- [ ] **Step 2: 에이전트 frontmatter name 일치 확인**

각 에이전트 파일의 `name:` 필드가 파일명과 일치하는지 확인.

```bash
for f in agents/expert-*.md; do
  filename=$(basename "$f" .md)
  name=$(grep '^name:' "$f" | sed 's/name: //')
  if [ "$filename" != "$name" ]; then
    echo "MISMATCH: $filename != $name"
  fi
done
```

Expected: 출력 없음 (전부 일치)

- [ ] **Step 3: SKILL.md에서 panels.md 참조 경로 확인**

```bash
grep -c 'references/panels.md' skills/expert-panel/SKILL.md
```

Expected: 1 이상
