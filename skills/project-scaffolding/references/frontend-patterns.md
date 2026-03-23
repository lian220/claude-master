# Frontend Architecture Patterns

## Table of Contents

1. [Next.js App Router Feature-Based 구조](#nextjs-app-router-feature-based-구조)
2. [컴포넌트 조직화](#컴포넌트-조직화)
3. [상태 관리 패턴](#상태-관리-패턴)
4. [데이터 페칭 패턴](#데이터-페칭-패턴)

---

## Next.js App Router Feature-Based 구조

참조: [next-shadcn-dashboard-starter](https://github.com/Kiranism/next-shadcn-dashboard-starter)

### 디렉토리 구조

```
src/
├── app/                          # App Router (라우팅 전용)
│   ├── (auth)/                   # 인증 레이아웃 그룹
│   │   ├── login/
│   │   │   └── page.tsx
│   │   ├── register/
│   │   │   └── page.tsx
│   │   └── layout.tsx
│   ├── (dashboard)/              # 대시보드 레이아웃 그룹
│   │   ├── overview/
│   │   │   └── page.tsx
│   │   ├── users/
│   │   │   ├── page.tsx
│   │   │   ├── [id]/
│   │   │   │   └── page.tsx
│   │   │   └── loading.tsx
│   │   └── layout.tsx
│   ├── api/                      # API Routes (BFF)
│   │   └── [...route]/
│   │       └── route.ts
│   ├── layout.tsx                # Root Layout
│   ├── loading.tsx               # Global Loading
│   └── error.tsx                 # Global Error
├── features/                     # 기능별 모듈 (핵심)
│   ├── auth/
│   │   ├── components/           # 기능 전용 컴포넌트
│   │   │   ├── login-form.tsx
│   │   │   └── register-form.tsx
│   │   ├── hooks/                # 기능 전용 훅
│   │   │   └── use-auth.ts
│   │   ├── actions/              # Server Actions
│   │   │   └── auth-actions.ts
│   │   ├── lib/                  # 기능 전용 유틸
│   │   │   └── auth-utils.ts
│   │   ├── types/                # 기능 전용 타입
│   │   │   └── auth.types.ts
│   │   └── index.ts              # Public API (barrel export)
│   ├── users/
│   │   ├── components/
│   │   │   ├── user-table.tsx
│   │   │   ├── user-form.tsx
│   │   │   └── user-card.tsx
│   │   ├── hooks/
│   │   │   └── use-users.ts
│   │   ├── actions/
│   │   │   └── user-actions.ts
│   │   ├── types/
│   │   │   └── user.types.ts
│   │   └── index.ts
│   └── dashboard/
│       ├── components/
│       ├── hooks/
│       └── index.ts
├── components/                   # 공유 UI 컴포넌트
│   ├── ui/                       # 기본 UI (shadcn/ui)
│   │   ├── button.tsx
│   │   ├── input.tsx
│   │   ├── dialog.tsx
│   │   └── ...
│   ├── layout/                   # 레이아웃 컴포넌트
│   │   ├── header.tsx
│   │   ├── sidebar.tsx
│   │   └── footer.tsx
│   └── shared/                   # 재사용 복합 컴포넌트
│       ├── data-table.tsx
│       ├── page-header.tsx
│       └── empty-state.tsx
├── hooks/                        # 공유 훅
│   ├── use-debounce.ts
│   ├── use-media-query.ts
│   └── use-local-storage.ts
├── lib/                          # 유틸리티
│   ├── utils.ts                  # 일반 유틸 (cn 함수 등)
│   ├── api-client.ts             # API 클라이언트
│   └── constants.ts              # 상수
├── types/                        # 전역 타입
│   └── global.d.ts
├── styles/                       # 전역 스타일
│   └── globals.css
└── config/                       # 앱 설정
    ├── site.ts                   # 사이트 메타데이터
    └── nav.ts                    # 네비게이션 설정
```

### 핵심 원칙

1. **app/ 디렉토리는 라우팅 전용**: 페이지 컴포넌트는 얇게, features에서 가져와 조합만 수행
2. **features/ 가 비즈니스 로직의 중심**: 기능별로 완전히 캡슐화
3. **components/ 는 기능 무관한 순수 UI만**: 비즈니스 로직 포함 금지
4. **barrel export**: 각 feature는 `index.ts`를 통해 public API만 노출

### 페이지 컴포넌트 패턴

```tsx
// app/(dashboard)/users/page.tsx
// 페이지는 얇게 - features에서 가져와 조합만 수행
import { UserTable } from '@/features/users';
import { PageHeader } from '@/components/shared/page-header';

export default async function UsersPage() {
  return (
    <div>
      <PageHeader title="Users" description="Manage users" />
      <UserTable />
    </div>
  );
}
```

---

## 컴포넌트 조직화

### 컴포넌트 분류 기준

| 분류 | 위치 | 특징 |
|------|------|------|
| UI 원자 (Atom) | `components/ui/` | 버튼, 인풋 등 기본 요소 |
| 공유 복합 (Molecule) | `components/shared/` | 데이터 테이블, 페이지 헤더 등 |
| 레이아웃 | `components/layout/` | 헤더, 사이드바, 푸터 |
| 기능 전용 | `features/{name}/components/` | 특정 기능에만 사용 |

### 컴포넌트 파일 네이밍

```
kebab-case.tsx           # 컴포넌트 파일
kebab-case.test.tsx      # 테스트 파일
kebab-case.stories.tsx   # 스토리북
use-kebab-case.ts        # 커스텀 훅
kebab-case.types.ts      # 타입 정의
```

### 컴포넌트 패턴

```tsx
// components/shared/data-table.tsx
'use client';

import { type ColumnDef } from '@tanstack/react-table';

interface DataTableProps<TData, TValue> {
  columns: ColumnDef<TData, TValue>[];
  data: TData[];
  searchKey?: string;
}

export function DataTable<TData, TValue>({
  columns,
  data,
  searchKey,
}: DataTableProps<TData, TValue>) {
  // 비즈니스 로직 없이 순수 UI 렌더링만
}
```

---

## 상태 관리 패턴

### 상태 분류

| 유형 | 도구 | 예시 |
|------|------|------|
| 서버 상태 | TanStack Query / SWR | API 데이터, 캐시 |
| URL 상태 | nuqs / useSearchParams | 필터, 페이지네이션, 정렬 |
| 폼 상태 | React Hook Form + Zod | 입력값, 유효성 검증 |
| UI 상태 | useState / useReducer | 모달 열림, 사이드바 토글 |
| 전역 상태 | Zustand (필요 시만) | 테마, 인증 정보 |

### 상태 관리 규칙

- Server State는 반드시 TanStack Query/SWR 사용 (직접 fetch + useState 금지)
- URL에 반영할 수 있는 상태는 URL 상태로 관리 (필터, 검색, 페이지)
- Zustand는 진정한 클라이언트 전역 상태에만 사용 (남용 금지)
- Context API는 prop drilling 해결용으로만 제한적 사용

---

## 데이터 페칭 패턴

### Server Component (기본)

```tsx
// features/users/components/user-table.tsx
import { getUsers } from '../actions/user-actions';

export async function UserTable() {
  const users = await getUsers();
  return <DataTable columns={columns} data={users} />;
}
```

### Server Action

```tsx
// features/users/actions/user-actions.ts
'use server';

import { revalidatePath } from 'next/cache';

export async function getUsers() {
  const res = await fetch(`${API_URL}/users`, {
    next: { tags: ['users'] },
  });
  return res.json();
}

export async function createUser(data: CreateUserInput) {
  const res = await fetch(`${API_URL}/users`, {
    method: 'POST',
    body: JSON.stringify(data),
  });
  revalidatePath('/users');
  return res.json();
}
```

### Client Component + TanStack Query

```tsx
// features/users/hooks/use-users.ts
'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

export function useUsers() {
  return useQuery({
    queryKey: ['users'],
    queryFn: () => fetch('/api/users').then(res => res.json()),
  });
}

export function useCreateUser() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: CreateUserInput) =>
      fetch('/api/users', { method: 'POST', body: JSON.stringify(data) }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['users'] }),
  });
}
```

### 데이터 페칭 선택 기준

| 요구사항 | 패턴 |
|----------|------|
| 초기 로딩 (SEO 필요) | Server Component + fetch |
| 사용자 인터랙션 후 갱신 | Server Action + revalidate |
| 실시간 업데이트 / 옵티미스틱 | Client Component + TanStack Query |
| 폼 제출 | Server Action 또는 useMutation |
