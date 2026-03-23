---
name: project-scaffolding
description: 프로젝트 구조 설계 및 스캐폴딩 전문 스킬. 신규 프로젝트 초기화, 기존 프로젝트 리팩토링, 아키텍처 패턴 적용을 지원. Backend(Hexagonal, Clean Architecture, DDD), Frontend(Feature-based, Route-based), Monorepo(Turborepo, Gradle multi-module) 구조를 다룸. 코딩 컨벤션, 린팅, 포맷팅, Git Hooks, CI/CD 설정 포함. "프로젝트 구조", "scaffolding", "보일러플레이트", "코드 구조", "아키텍처 셋업", "project setup", "init project", "프로젝트 초기화", "디렉토리 구조", "패키지 구조", "모듈 구조", "monorepo", "모노레포" 키워드에 반응.
---

# Project Scaffolding

## 개요

프로젝트 유형을 분석하고, 업계 표준 아키텍처 패턴에 기반한 프로젝트 구조를 추천/생성하는 스킬.

## 워크플로우

### 1단계: 프로젝트 분석

사용자에게 다음 정보를 확인:

- **프로젝트 유형**: Backend / Frontend / Fullstack / Monorepo
- **기술 스택**: Spring Boot + Kotlin, Next.js, FastAPI 등
- **아키텍처 패턴**: Hexagonal, Clean, Layered, Feature-based 등
- **신규 vs 기존**: 새로 만들기 / 기존 구조 리팩토링

사용자가 명시하지 않은 경우, 프로젝트 루트의 파일(`build.gradle.kts`, `package.json`, `pyproject.toml` 등)을 분석하여 자동 감지.

### 2단계: 아키텍처 패턴 선택

프로젝트 유형에 따라 적절한 참조 문서 로드:

| 프로젝트 유형 | 참조 문서 |
|--------------|----------|
| Backend (Spring Boot, FastAPI 등) | [references/backend-patterns.md](references/backend-patterns.md) |
| Frontend (Next.js, React 등) | [references/frontend-patterns.md](references/frontend-patterns.md) |
| Monorepo (Turborepo, Gradle) | [references/monorepo-patterns.md](references/monorepo-patterns.md) |

### 3단계: 구조 생성/리팩토링

#### 신규 프로젝트

1. 디렉토리 구조 생성 (`mkdir -p`)
2. 기본 설정 파일 생성 (`.editorconfig`, `.gitignore`, lint 설정 등)
3. 빌드 설정 파일 생성 (`build.gradle.kts`, `package.json` 등)
4. README 템플릿 생성

#### 기존 프로젝트 리팩토링

1. 현재 구조 분석 (`find` 또는 `tree`)
2. 목표 구조와 차이점 도출
3. 단계별 마이그레이션 계획 제시
4. 사용자 확인 후 실행

### 4단계: 공통 설정 적용

#### 코드 품질 도구

| 스택 | 린터 | 포맷터 |
|------|------|--------|
| Kotlin | ktlint | ktlint |
| TypeScript | ESLint | Prettier |
| Python | ruff | ruff |

#### Git Hooks (Husky / pre-commit)

```yaml
# .pre-commit-config.yaml (Python)
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.4.0
    hooks:
      - id: ruff
      - id: ruff-format
```

```json
// package.json (Node.js)
{
  "husky": {
    "hooks": {
      "pre-commit": "lint-staged"
    }
  }
}
```

#### EditorConfig

```ini
# .editorconfig
root = true

[*]
indent_style = space
indent_size = 4
end_of_line = lf
charset = utf-8
trim_trailing_whitespace = true
insert_final_newline = true

[*.{ts,tsx,js,jsx,json,yaml,yml}]
indent_size = 2

[*.md]
trim_trailing_whitespace = false
```

## 규칙

### 네이밍 컨벤션

| 대상 | 규칙 | 예시 |
|------|------|------|
| 디렉토리 | kebab-case | `user-management/` |
| Kotlin 패키지 | lowercase dot-separated | `com.example.user` |
| TypeScript 모듈 | kebab-case | `use-auth.ts` |
| Python 모듈 | snake_case | `user_service.py` |

### 금지 사항

- 순환 의존성 생성 금지
- 도메인 레이어에서 프레임워크 의존성 금지 (Hexagonal/Clean Architecture)
- 비즈니스 로직을 Controller/Router에 직접 작성 금지
- `src/` 없이 루트에 소스 파일 배치 금지

### 필수 파일

모든 프로젝트에 다음 파일 포함:

- `.gitignore` (스택별 적절한 내용)
- `.editorconfig`
- `README.md` (프로젝트 소개, 실행 방법, 구조 설명)

## CI/CD 기본 설정

### GitHub Actions 템플릿

```yaml
# .github/workflows/ci.yml
name: CI
on:
  pull_request:
    branches: [main, develop]
  push:
    branches: [main, develop]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Setup
        # 스택별 설정
      - name: Lint
        # 스택별 린트
      - name: Test
        # 스택별 테스트
      - name: Build
        # 스택별 빌드
```
