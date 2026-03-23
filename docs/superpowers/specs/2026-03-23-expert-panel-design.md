# Expert Panel Design Spec

> 최신 트렌드를 리서치하는 분야별 전문가 패널 리뷰 시스템

## 개요

`/expert-panel` 스킬은 주제에 맞는 전문가 에이전트를 병렬로 실행하여 다각도 리뷰를 수행한다. 각 전문가는 리뷰 전 WebSearch로 최신 트렌드를 리서치한 뒤, 그 기준으로 검토하고, 결과를 통합 리포트로 제공한다.

## 구조

```
skills/expert-panel/
  SKILL.md                        ← 오케스트레이터 (패널 파싱, 자동 추천, 결과 통합)
  references/
    panels.md                     ← 5개 패널 정의 + 전문가 매핑
    expert-prompts.md             ← 15명 전문가 페르소나 상세
    report-template.md            ← 통합 리포트 형식

agents/experts/
  ui-ux-designer.md               ← UI/UX 전문가
  visual-designer.md              ← 비주얼 디자인 전문가
  ia-specialist.md                ← IA/화면설계 전문가
  frontend-architect.md           ← 프론트엔드 아키텍트
  frontend-performance.md         ← 프론트엔드 성능 전문가
  a11y-specialist.md              ← 접근성(a11y) 전문가
  backend-architect.md            ← 백엔드 아키텍트
  security-expert.md              ← 보안 전문가
  db-performance-expert.md        ← DB/성능 전문가
  devops-engineer.md              ← DevOps 엔지니어
  cloud-architect.md              ← 클라우드 아키텍트
  sre-expert.md                   ← SRE 전문가
  strategy-expert.md              ← 전략 전문가
  marketing-expert.md             ← 마케팅/그로스 전문가
  pm-planner.md                   ← PM/기획자
```

## 사용법

### 자동 선택 (기본)
```bash
/expert-panel "결제 플로우가 복잡한 것 같아"
```
→ AI가 주제를 분석하여 적합한 전문가 추천
→ "UX 전문가, 전략 전문가, 프론트엔드 아키텍트를 투입하겠습니다. 진행할까요?"
→ 사용자 확인 후 실행

### 직접 지정 (오버라이드)
```bash
/expert-panel --experts "보안,백엔드아키텍트" "인증 로직 검토"
```
→ 지정된 전문가로 바로 실행

### 패널 단위 지정
```bash
/expert-panel --panels "frontend,business" "랜딩페이지 검토"
```
→ 해당 패널의 전문가 전체 투입

### 전체 투입
```bash
/expert-panel --all "서비스 런칭 전 종합 검토"
```

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

## 2단계: 검토 기준 수립
- 기본 체크리스트 + 트렌드 기반 동적 체크리스트 결합

## 3단계: 대상 분석
- 코드/문서/화면 검토
- 체크리스트 기반 항목별 평가

## 4단계: 리포트 작성
- 표준 형식으로 출력 (아래 형식 준수)

# 기본 체크리스트
- [ ] {분야별 체크 항목들}

# 출력 형식
🔴 Critical: 즉시 수정 필요
🟡 Warning: 개선 권장
🟢 Good: 잘 된 점
💡 Trend Insight: 최신 트렌드 기반 제안 (출처 포함)
```

## 스킬 실행 플로우

```
사용자 입력
    │
    ▼
1. 입력 파싱
   ├── --experts 플래그 있음 → 지정된 전문가 목록 확정
   ├── --panels 플래그 있음 → 패널 내 전문가 전체 확정
   ├── --all 플래그 있음 → 15명 전체 확정
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
   ├── 확정된 전문가 에이전트를 Agent 도구로 병렬 실행
   ├── 각 에이전트에게 주제 + 검토 대상 전달
   └── 각 에이전트가 독립적으로 리서치 → 검토 → 리포트
    │
    ▼
4. 결과 통합
   ├── 각 에이전트 리포트 수집
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

- **기존 에이전트** (code-reviewer, security-sentinel 등): 그대로 유지. expert-panel은 별도 시스템
- **agent-teams 커맨드**: 기존 프리셋(review, fullstack, quality, debug) 유지. expert-panel은 독립 스킬
- **향후 확장**: 필요시 새 전문가 에이전트 파일만 추가하고 panels.md에 등록하면 됨
