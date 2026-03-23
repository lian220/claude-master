# Expert Panel Design Spec

> 최신 트렌드를 리서치하는 분야별 전문가 패널 리뷰 시스템

## 개요

`/expert-panel` 스킬은 주제에 맞는 전문가 에이전트를 병렬로 실행하여 다각도 리뷰를 수행한다. 각 전문가는 리뷰 전 WebSearch로 최신 트렌드를 리서치한 뒤, 그 기준으로 검토하고, 결과를 통합 리포트로 제공한다.

## 구조

```
skills/expert-panel/
  SKILL.md                        ← 오케스트레이터 (패널 파싱, 자동 추천, 결과 통합)
  references/
    panels.md                     ← 5개 패널 정의 + 전문가 매핑 + 별칭 테이블

agents/                           ← 기존 에이전트와 같은 레벨에 expert- 접두사로 배치
  expert-ui-ux-designer.md
  expert-visual-designer.md
  expert-ia-specialist.md
  expert-frontend-architect.md
  expert-frontend-performance.md
  expert-a11y-specialist.md
  expert-backend-architect.md
  expert-security.md
  expert-db-performance.md
  expert-devops.md
  expert-cloud-architect.md
  expert-sre.md
  expert-strategy.md
  expert-marketing.md
  expert-pm-planner.md
```

> **디렉토리 결정 근거**: 기존 에이전트(code-reviewer.md, debugger.md 등)가 `agents/` 루트에 플랫하게 배치되어 있으므로 동일 패턴을 따른다. `expert-` 접두사로 기존 에이전트와 구분한다.

## SKILL.md 정의

```yaml
---
name: expert-panel
description: >
  분야별 전문가 패널 병렬 리뷰 시스템. 최신 트렌드를 리서치한 뒤 전문가 관점에서 검토.
  "전문가 리뷰", "expert panel", "패널 리뷰", "다각도 검토", "종합 분석" 키워드에 반응.
  코드/설계/기획/화면을 여러 전문가 관점에서 동시에 검토할 때 사용.
---
```

**SKILL.md body 구조:**
1. 입력 파싱 (플래그 처리, 별칭 매핑)
2. 자동 추천 로직 (플래그 없을 때)
3. 사용자 확인 게이트
4. 병렬 에이전트 디스패치 (배치 전략 포함)
5. 결과 통합 및 리포트 생성
6. panels.md 참조 지시

## 사용법

### 자동 선택 (기본)
```bash
/expert-panel "결제 플로우가 복잡한 것 같아"
```
→ AI가 주제를 분석하여 적합한 전문가 추천
→ "UX 전문가, 전략 전문가, 프론트엔드 아키텍트를 투입하겠습니다. 진행할까요?"
→ 사용자 확인/수정 후 실행

### 직접 지정 (오버라이드)
```bash
/expert-panel --experts "security,backend-architect" "인증 로직 검토"
```
→ 에이전트 ID(expert- 접두사 생략 가능)로 지정, 바로 실행

### 패널 단위 지정
```bash
/expert-panel --panels "frontend,business" "랜딩페이지 검토"
```
→ 해당 패널의 전문가 전체 투입

### 전체 투입
```bash
/expert-panel --all "서비스 런칭 전 종합 검토"
```
→ 5개씩 3배치로 순차 실행 (아래 배치 전략 참조)

## 전문가 별칭 매핑

`--experts` 플래그는 에이전트 ID의 `expert-` 접두사를 생략한 형태를 사용한다. panels.md에 별칭 테이블을 정의하여 한글 매핑도 지원한다.

| 별칭 (한글) | 별칭 (영문 약어) | 에이전트 ID |
|------------|----------------|-----------|
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

**매칭 우선순위**: 에이전트 ID 정확 매치 → 영문 별칭 → 한글 별칭

## 5개 패널 구성

### 1. ui — 화면/UI 패널
| 전문가 | 에이전트 ID | 핵심 역할 |
|--------|-----------|---------|
| UI/UX 디자이너 | expert-ui-ux-designer | 사용성, 접근성, 인터랙션 패턴 |
| 비주얼 디자인 전문가 | expert-visual-designer | 컬러, 타이포, 레이아웃 일관성 |
| IA/화면설계 전문가 | expert-ia-specialist | 정보 구조, 네비게이션 플로우 |

### 2. frontend — 프론트엔드 패널
| 전문가 | 에이전트 ID | 핵심 역할 |
|--------|-----------|---------|
| 프론트엔드 아키텍트 | expert-frontend-architect | 컴포넌트 설계, 상태관리 |
| 성능 전문가 | expert-frontend-performance | 번들 사이즈, Core Web Vitals |
| 접근성 전문가 | expert-a11y-specialist | WCAG, 스크린리더 호환 |

### 3. backend — 백엔드 패널
| 전문가 | 에이전트 ID | 핵심 역할 |
|--------|-----------|---------|
| 백엔드 아키텍트 | expert-backend-architect | 도메인 설계, Hexagonal, CQRS |
| 보안 전문가 | expert-security | OWASP, 인증/인가, 취약점 |
| DB/성능 전문가 | expert-db-performance | 쿼리 최적화, 인덱싱, 캐싱 |

### 4. infra — 인프라 패널
| 전문가 | 에이전트 ID | 핵심 역할 |
|--------|-----------|---------|
| DevOps 엔지니어 | expert-devops | CI/CD, 배포 전략, 모니터링 |
| 클라우드 아키텍트 | expert-cloud-architect | 비용 최적화, 확장성, HA |
| SRE | expert-sre | 장애 대응, 옵저버빌리티 |

### 5. business — 비즈니스/기획 패널
| 전문가 | 에이전트 ID | 핵심 역할 |
|--------|-----------|---------|
| 전략 전문가 | expert-strategy | PMF, 비즈니스 모델, 경쟁 분석 |
| 마케팅 전문가 | expert-marketing | 전환율, CTA, 퍼널 |
| PM/기획자 | expert-pm-planner | 사용자 스토리, 요구사항 검증 |

## 에이전트 공통 구조

각 전문가의 상세 페르소나와 체크리스트는 에이전트 `.md` 파일 자체가 source of truth이다. panels.md는 매핑/별칭 정보만 관리한다.

```markdown
---
name: expert-{id}
description: {한글 설명}
tools: Read, Grep, Glob, Bash, WebSearch, WebFetch
model: sonnet
---

# 역할
{상세 페르소나: 경력, 전문 분야, 배경}

# 실행 프로세스

## 1단계: 트렌드 리서치
- WebSearch로 해당 분야 최신 트렌드 2-3개 쿼리 검색
- 검색 결과에서 핵심 기준/벤치마크 추출
- 출처 URL 기록
- **폴백**: WebSearch 실패 시 기본 체크리스트만으로 진행. 리포트에 "트렌드 리서치 불가" 명시.

## 2단계: 검토 기준 수립
- 기본 체크리스트 + 트렌드 기반 동적 체크리스트 결합

## 3단계: 대상 분석
- 코드/문서/화면 검토
- 체크리스트 기반 항목별 평가

## 4단계: 리포트 작성
- 표준 형식으로 출력 (아래 형식 준수)
- 리포트는 간결하게 작성 (최대 800 토큰 이내 권장)

# 기본 체크리스트
- [ ] {분야별 체크 항목들}

# 출력 형식
🔴 Critical: 즉시 수정 필요
🟡 Warning: 개선 권장
🟢 Good: 잘 된 점
💡 Trend Insight: 최신 트렌드 기반 제안 (출처 포함)
```

> **모델 선택 근거**: 비용 효율과 속도를 위해 전체 sonnet 기본값. 전문가별로 필요시 개별 에이전트 파일에서 `model: opus`로 오버라이드 가능.

## 병렬 실행 배치 전략

| 투입 인원 | 실행 방식 |
|----------|---------|
| 1-5명 | 전원 동시 병렬 실행 |
| 6-10명 | 5명씩 2배치 순차 실행 |
| 11-15명 | 5명씩 3배치 순차 실행 |

- 각 배치의 모든 에이전트가 완료된 후 다음 배치 실행
- 개별 에이전트 타임아웃: 3분. 초과 시 해당 에이전트 결과 없이 통합 리포트에 "타임아웃" 표기
- `--all` 사용 시 사전 경고: "15명 전체 투입은 시간이 걸릴 수 있습니다. 진행할까요?"

## 스킬 실행 플로우

```
사용자 입력
    │
    ▼
1. 입력 파싱
   ├── --experts 플래그 있음 → 별칭 테이블로 에이전트 ID 매핑 → 확정
   ├── --panels 플래그 있음 → 패널 내 전문가 전체 확정
   ├── --all 플래그 있음 → 15명 전체 확정 (경고 메시지 출력)
   └── 플래그 없음 → 2단계로
    │
    ▼
2. 자동 추천 (플래그 없는 경우)
   ├── 주제 분석하여 적합한 전문가 3-5명 선정
   ├── 선정 이유와 함께 사용자에게 제시
   └── 사용자 확인/수정 후 확정
    │
    ▼
3. 병렬 에이전트 디스패치
   ├── 배치 전략에 따라 에이전트 실행
   ├── 각 에이전트에게 주제 + 검토 대상 전달
   └── 각 에이전트가 독립적으로 리서치 → 검토 → 리포트
    │
    ▼
4. 결과 통합
   ├── 각 에이전트 리포트 수집 (타임아웃 에이전트 표기)
   ├── 중복 제거 및 우선순위 정리
   ├── 통합 리포트 생성
   └── 액션 아이템 도출
```

## 통합 리포트 형식

```markdown
# Expert Panel Report
> 주제: "{사용자 입력 주제}"
> 투입 전문가: {전문가 목록}
> 날짜: {실행일}

---

## 종합 요약
| 등급 | 개수 |
|------|------|
| 🔴 Critical | N |
| 🟡 Warning | N |
| 🟢 Good | N |
| 💡 Trend Insight | N |

## 🔴 Critical (즉시 조치)
1. [{전문가}] {내용}

## 🟡 Warning (개선 권장)
1. [{전문가}] {내용}

## 💡 Trend Insights (최신 트렌드 기반)
1. [{전문가}] {트렌드 인사이트} (출처: {URL})

## 🟢 Good (잘 된 점)
1. [{전문가}] {내용}

## 액션 아이템 (우선순위순)
1. [ ] {실행 가능한 개선 사항}
```

## 기존 시스템과의 관계

| 상황 | 사용할 도구 |
|------|-----------|
| PR 전 코드 품질/보안/버그 빠른 체크 | `/agent-teams review` (기존) |
| 최신 트렌드 기반 다각도 심층 리뷰 | `/expert-panel` (신규) |
| 개별 전문가 의견이 필요할 때 | `@expert-{id}` 직접 호출 |

- **기존 에이전트** (code-reviewer, security-sentinel 등): 그대로 유지
- **agent-teams 커맨드**: 기존 프리셋(review, fullstack, quality, debug) 유지
- **향후 확장**: 새 전문가 에이전트 파일을 `agents/` 에 추가하고 `panels.md`의 매핑 테이블에 등록

## panels.md 구조

panels.md는 패널-전문가 매핑과 별칭 테이블만 관리한다 (페르소나 상세는 에이전트 파일이 source of truth).

```yaml
panels:
  ui:
    name: "화면/UI 패널"
    experts: [expert-ui-ux-designer, expert-visual-designer, expert-ia-specialist]
  frontend:
    name: "프론트엔드 패널"
    experts: [expert-frontend-architect, expert-frontend-performance, expert-a11y-specialist]
  backend:
    name: "백엔드 패널"
    experts: [expert-backend-architect, expert-security, expert-db-performance]
  infra:
    name: "인프라 패널"
    experts: [expert-devops, expert-cloud-architect, expert-sre]
  business:
    name: "비즈니스/기획 패널"
    experts: [expert-strategy, expert-marketing, expert-pm-planner]

aliases:
  # 한글 별칭
  UX: expert-ui-ux-designer
  보안: expert-security
  마케팅: expert-marketing
  # ... (전체 별칭 테이블)
```
