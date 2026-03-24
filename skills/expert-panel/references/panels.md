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

## 매칭 로직

1. 입력값에서 `expert-` 접두사 생략 시 자동 추가 (예: `security` → `expert-security`)
2. 매칭 우선순위: 에이전트 ID 정확 매치 → 영문 별칭 → 한글 별칭
