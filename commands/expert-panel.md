# Expert Panel (전문가 패널 리뷰)

**사용법**: `/expert-panel [옵션] [주제]`

분야별 전문가 에이전트를 병렬로 실행하여 최신 트렌드 기반 다각도 리뷰를 수행합니다.

## 인자

- `--experts "a,b,c"` — 전문가 직접 지정
- `--panels "x,y"` — 패널 단위 지정
- `--all` — 전체 15명 투입
- 옵션 없음 — AI가 주제 분석 후 자동 추천

$ARGUMENTS

## 실행 프로세스

### Step 1: 입력 파싱

`$ARGUMENTS`에서 플래그와 주제를 분리한다.

**전문가 ID 매칭** (`skills/expert-panel/references/panels.md` 참조):

1. `expert-`로 시작하면 그대로 사용
2. `expert-` 접두사 없으면 자동 추가 (예: `security` → `expert-security`)
3. 영문 별칭 매칭 (예: `fe-arch` → `expert-frontend-architect`)
4. 한글 별칭 매칭 (예: `보안` → `expert-security`)

### Step 2: 전문가 선정

**자동 추천 모드 (옵션 없음):**

주제를 분석하여 적합한 전문가 3-5명을 선정. 사용자에게 제시:

```
주제를 분석한 결과, 다음 전문가를 투입하겠습니다:

| 전문가 | 선정 이유 |
|--------|---------|
| @expert-ui-ux-designer | 사용자 플로우 관련 UX 검토 필요 |
| @expert-frontend-architect | 프론트엔드 구조 검증 필요 |
| @expert-strategy | 비즈니스 관점 검토 필요 |

진행할까요? (전문가를 추가/제거하려면 알려주세요)
```

**사용자 확인을 받은 후에만 다음 단계로 진행한다.**

**직접 지정 (`--experts`)**: 별칭 매핑 후 바로 Step 3.
**패널 단위 (`--panels`)**: 해당 패널 전문가 전체 투입.
**전체 (`--all`)**: "15명 전체 투입은 시간이 걸릴 수 있습니다. 진행할까요?" 경고 후 진행.

### Step 3: 병렬 에이전트 디스패치

**배치 전략:**

| 투입 인원 | 실행 방식 |
|----------|---------|
| 1-5명 | 전원 동시 병렬 실행 |
| 6-10명 | 5명씩 2배치 순차 실행 |
| 11-15명 | 5명씩 3배치 순차 실행 |

각 전문가를 Agent 도구로 호출한다:

```
Agent 도구 호출:
  subagent_type: {에이전트 ID}  (예: expert-security)
  prompt: |
    검토 주제: {사용자가 입력한 주제}
    검토 대상: {관련 파일 경로 또는 설명}

    위 주제에 대해 당신의 전문 분야 관점에서 검토해주세요.
    Phase 1-4 프로세스를 따라 실행하고, 출력 형식에 맞춰 리포트를 작성해주세요.
```

**같은 배치 내의 에이전트는 반드시 하나의 메시지에서 병렬로 호출한다.**

### Step 4: 결과 통합

모든 에이전트 리포트를 수집하여 통합 리포트를 생성:

```
## Expert Panel Report
> 주제: "{주제}"
> 투입 전문가: {목록}
> 날짜: {실행일}

### 종합 요약
| 등급 | 개수 |
|------|------|
| 🔴 Critical | N |
| 🟡 Warning | N |
| 🟢 Good | N |
| 💡 Trend Insight | N |

### 🔴 Critical (즉시 조치)
1. [{전문가}] {내용}

### 🟡 Warning (개선 권장)
1. [{전문가}] {내용}

### 💡 Trend Insights (최신 트렌드 기반)
1. [{전문가}] {인사이트} (출처: {URL})

### 🟢 Good (잘 된 점)
1. [{전문가}] {내용}

### 액션 아이템 (우선순위순)
1. [ ] {실행 가능한 개선 사항}
```

**통합 규칙:**
- 동일 이슈 → 하나로 합치고 전문가 모두 태그
- Critical > Warning > Trend Insight > Good 순서
- 미응답 에이전트 → "⏱ {전문가}: 응답 없음" 표기

## 5개 패널

| 패널 | 전문가 |
|------|--------|
| **ui** | @expert-ui-ux-designer, @expert-visual-designer, @expert-ia-specialist |
| **frontend** | @expert-frontend-architect, @expert-frontend-performance, @expert-a11y-specialist |
| **backend** | @expert-backend-architect, @expert-security, @expert-db-performance |
| **infra** | @expert-devops, @expert-cloud-architect, @expert-sre |
| **business** | @expert-strategy, @expert-marketing, @expert-pm-planner |

## 사용 예시

```bash
/expert-panel "결제 플로우가 복잡해"                          # 자동 추천
/expert-panel --experts "ux,fe-arch,marketing" "랜딩페이지"    # 직접 지정
/expert-panel --panels "frontend,business" "서비스 검토"       # 패널 단위
/expert-panel --panels "ui" "메인 화면 디자인"                 # UI 패널만
/expert-panel --all "런칭 전 종합 검토"                        # 전체 투입
```
