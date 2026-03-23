# Monorepo Patterns

## Table of Contents

1. [Turborepo (Frontend Monorepo)](#turborepo-frontend-monorepo)
2. [Gradle Multi-Module (Backend Monorepo)](#gradle-multi-module-backend-monorepo)
3. [Fullstack Monorepo](#fullstack-monorepo)
4. [공유 설정 패턴](#공유-설정-패턴)

---

## Turborepo (Frontend Monorepo)

### 디렉토리 구조

```
project-root/
├── turbo.json                    # Turborepo 파이프라인 설정
├── package.json                  # 루트 (워크스페이스 설정)
├── pnpm-workspace.yaml           # pnpm 워크스페이스
├── apps/
│   ├── web/                      # 메인 웹 앱 (Next.js)
│   │   ├── package.json
│   │   ├── next.config.ts
│   │   └── src/
│   ├── admin/                    # 어드민 앱 (Next.js)
│   │   ├── package.json
│   │   └── src/
│   └── docs/                     # 문서 사이트
│       ├── package.json
│       └── src/
├── packages/
│   ├── ui/                       # 공유 UI 컴포넌트 라이브러리
│   │   ├── package.json
│   │   ├── src/
│   │   │   ├── button.tsx
│   │   │   ├── input.tsx
│   │   │   └── index.ts
│   │   └── tsconfig.json
│   ├── lib/                      # 공유 유틸리티
│   │   ├── package.json
│   │   └── src/
│   ├── types/                    # 공유 타입 정의
│   │   ├── package.json
│   │   └── src/
│   └── api-client/               # API 클라이언트 (공유)
│       ├── package.json
│       └── src/
├── tooling/                      # 공유 개발 도구 설정
│   ├── eslint/                   # ESLint 공유 설정
│   │   ├── package.json
│   │   ├── base.js
│   │   ├── next.js
│   │   └── react.js
│   ├── typescript/               # TypeScript 공유 설정
│   │   ├── package.json
│   │   ├── base.json
│   │   ├── nextjs.json
│   │   └── react-library.json
│   └── prettier/                 # Prettier 공유 설정
│       ├── package.json
│       └── index.js
└── .github/
    └── workflows/
        └── ci.yml
```

### 핵심 설정 파일

#### turbo.json

```json
{
  "$schema": "https://turbo.build/schema.json",
  "globalDependencies": ["**/.env.*local"],
  "tasks": {
    "build": {
      "dependsOn": ["^build"],
      "outputs": [".next/**", "!.next/cache/**", "dist/**"]
    },
    "lint": {
      "dependsOn": ["^build"]
    },
    "dev": {
      "cache": false,
      "persistent": true
    },
    "test": {
      "dependsOn": ["^build"]
    },
    "type-check": {
      "dependsOn": ["^build"]
    }
  }
}
```

#### pnpm-workspace.yaml

```yaml
packages:
  - "apps/*"
  - "packages/*"
  - "tooling/*"
```

#### 패키지 참조 방법

```json
// apps/web/package.json
{
  "dependencies": {
    "@repo/ui": "workspace:*",
    "@repo/lib": "workspace:*",
    "@repo/types": "workspace:*"
  },
  "devDependencies": {
    "@repo/eslint-config": "workspace:*",
    "@repo/typescript-config": "workspace:*"
  }
}
```

### 패키지 네이밍 규칙

| 위치 | 스코프 | 예시 |
|------|--------|------|
| `apps/` | `@app/` 또는 이름 그대로 | `web`, `admin` |
| `packages/` | `@repo/` | `@repo/ui`, `@repo/lib` |
| `tooling/` | `@repo/` | `@repo/eslint-config` |

---

## Gradle Multi-Module (Backend Monorepo)

### MSA 스타일 멀티모듈

```
project-root/
├── build.gradle.kts              # 루트 빌드 (공통 설정)
├── settings.gradle.kts           # 모듈 등록
├── gradle/
│   └── libs.versions.toml        # Version Catalog
├── buildSrc/                     # 빌드 컨벤션 플러그인
│   ├── build.gradle.kts
│   └── src/main/kotlin/
│       └── conventions/
│           ├── kotlin-base.gradle.kts
│           ├── spring-boot-app.gradle.kts
│           └── spring-boot-lib.gradle.kts
├── shared/                       # 공유 모듈
│   ├── shared-domain/            # 공유 도메인 객체
│   ├── shared-infra/             # 공유 인프라 (로깅, 모니터링)
│   └── shared-test/              # 공유 테스트 유틸
├── service-user/                 # 사용자 서비스
│   ├── user-domain/
│   ├── user-application/
│   ├── user-infra/
│   └── user-api/
├── service-order/                # 주문 서비스
│   ├── order-domain/
│   ├── order-application/
│   ├── order-infra/
│   └── order-api/
└── gateway/                      # API Gateway
    └── build.gradle.kts
```

### settings.gradle.kts

```kotlin
rootProject.name = "my-platform"

// 공유 모듈
include("shared:shared-domain")
include("shared:shared-infra")
include("shared:shared-test")

// 사용자 서비스
include("service-user:user-domain")
include("service-user:user-application")
include("service-user:user-infra")
include("service-user:user-api")

// 주문 서비스
include("service-order:order-domain")
include("service-order:order-application")
include("service-order:order-infra")
include("service-order:order-api")

// Gateway
include("gateway")
```

### 빌드 컨벤션 플러그인

```kotlin
// buildSrc/src/main/kotlin/conventions/kotlin-base.gradle.kts
plugins {
    kotlin("jvm")
}

group = "com.example"

kotlin {
    jvmToolchain(21)
}

tasks.test {
    useJUnitPlatform()
}
```

```kotlin
// buildSrc/src/main/kotlin/conventions/spring-boot-lib.gradle.kts
plugins {
    id("conventions.kotlin-base")
    kotlin("plugin.spring")
}

// 라이브러리 모듈: bootJar 비활성화
tasks.named<org.springframework.boot.gradle.tasks.bundling.BootJar>("bootJar") {
    enabled = false
}

tasks.named<Jar>("jar") {
    enabled = true
}
```

---

## Fullstack Monorepo

### 구조 (Backend + Frontend 통합)

```
project-root/
├── README.md
├── docker-compose.yml
├── .github/
│   └── workflows/
│       ├── backend-ci.yml
│       ├── frontend-ci.yml
│       └── deploy.yml
├── backend/                      # Gradle 멀티모듈
│   ├── build.gradle.kts
│   ├── settings.gradle.kts
│   ├── gradle/
│   │   └── libs.versions.toml
│   ├── core-domain/
│   ├── core-application/
│   ├── infra-persistence/
│   └── api-rest/
├── frontend/                     # Turborepo 또는 단일 Next.js
│   ├── package.json
│   ├── turbo.json                # (Turborepo 사용 시)
│   ├── apps/
│   │   └── web/
│   └── packages/
│       └── ui/
├── deploy/                       # 배포 설정
│   ├── k8s/
│   ├── terraform/
│   └── docker/
├── docs/                         # 프로젝트 문서
│   ├── architecture/
│   ├── api/
│   └── decisions/
└── scripts/                      # 개발 스크립트
    ├── setup.sh
    └── seed-db.sh
```

### CI/CD 분리 전략

```yaml
# .github/workflows/backend-ci.yml
on:
  push:
    paths:
      - 'backend/**'
      - '.github/workflows/backend-ci.yml'

# .github/workflows/frontend-ci.yml
on:
  push:
    paths:
      - 'frontend/**'
      - '.github/workflows/frontend-ci.yml'
```

---

## 공유 설정 패턴

### .gitignore (루트)

```gitignore
# IDE
.idea/
.vscode/
*.iml

# OS
.DS_Store
Thumbs.db

# Environment
.env
.env.local
.env.*.local

# Build
build/
dist/
.next/
out/
node_modules/

# Test
coverage/

# Logs
*.log
```

### Docker Compose (개발용)

```yaml
# docker-compose.yml
services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: mydb
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

volumes:
  postgres_data:
```

### Makefile (개발 편의)

```makefile
.PHONY: help setup dev test lint clean

help: ## 도움말 표시
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

setup: ## 프로젝트 초기 설정
	@echo "Setting up project..."
	cd backend && ./gradlew build
	cd frontend && pnpm install

dev: ## 개발 서버 실행
	docker compose up -d
	cd backend && ./gradlew bootRun &
	cd frontend && pnpm dev

test: ## 전체 테스트 실행
	cd backend && ./gradlew test
	cd frontend && pnpm test

lint: ## 린트 실행
	cd backend && ./gradlew ktlintCheck
	cd frontend && pnpm lint

clean: ## 빌드 산출물 정리
	cd backend && ./gradlew clean
	cd frontend && pnpm clean
```
