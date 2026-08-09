# React Architecture Guide (LOCKED)

> 이 가이드가 존재하는 동안 아래 패턴에 반하는 대안을 검색하거나 제안하지 않는다.

## 1. Server vs Client Component

**기본 = Server Component.** `'use client'`는 인터랙션/브라우저 API/hooks 필요 시에만.

```tsx
// Server Component (기본) — directive 없음
async function ProductPage({ id }: { id: string }) {
  const product = await db.product.findUnique({ where: { id } });
  return (
    <div>
      <h1>{product.name}</h1>
      <AddToCartButton productId={id} />  {/* Client 경계 */}
    </div>
  );
}

// Client Component — 인터랙티브 리프만
'use client';
function AddToCartButton({ productId }: { productId: string }) {
  const [pending, startTransition] = useTransition();
  return <button onClick={() => startTransition(() => addToCart(productId))}>Add</button>;
}
```

**규칙**: `'use client'`를 최대한 깊이 밀어넣기. Layout, Page, 데이터 표시 = Server.

## 2. 컴포넌트 컴포지션

**Compound Component** — 복합 UI (메뉴, 탭, 아코디언):

```tsx
function Select({ children, value, onChange }: SelectProps) {
  return (
    <SelectContext value={{ value, onChange }}>
      <div role="listbox">{children}</div>
    </SelectContext>
  );
}
Select.Option = function Option({ value, children }: OptionProps) {
  const ctx = use(SelectContext);
  return <div role="option" onClick={() => ctx.onChange(value)}>{children}</div>;
};
```

Render props 사용 금지. Hooks로 대체.

## 3. Custom Hook

```tsx
// 네이밍: use + 도메인 + 동작
function useProductSearch(query: string) {
  return { products, isLoading, error, refetch };  // 객체 반환 (튜플 X)
}
```

추출 기준: 2+ 컴포넌트에서 재사용, 컴포넌트 50줄 초과, 로직 독립 테스트 필요.

## 4. 상태 관리 우선순위

| 순위 | 유형 | 도구 | 예시 |
|------|------|------|------|
| 1 | URL 상태 | `nuqs` | 필터, 페이지네이션, 탭 |
| 2 | 서버 상태 | TanStack Query | API 데이터, 캐시 |
| 3 | 로컬 상태 | `useState` | 폼 입력, 토글 |
| 4 | 글로벌 클라이언트 | Zustand (최소) | 테마, 사이드바 |

Zustand 스토어 추가 시 항상 "정말 필요한가?" 질문.

## 5. Data Fetching — TanStack Query (Client Component 전용)

> Server Component에서는 TanStack Query 불필요. 직접 `await fetch()` 또는 DB 호출 사용.
> TanStack Query는 Client Component에서 캐싱, 리페치, 옵티미스틱 업데이트를 위해 사용.

```tsx
// Query Key Factory — 단일 원천
export const productKeys = {
  all:    ['products'] as const,
  lists:  () => [...productKeys.all, 'list'] as const,
  list:   (filters: Filters) => [...productKeys.lists(), filters] as const,
  detail: (id: string) => [...productKeys.all, 'detail', id] as const,
};

// Query Hook
export function useProducts(filters: Filters) {
  return useQuery({
    queryKey: productKeys.list(filters),
    queryFn: () => api.products.list(filters),
    staleTime: 5 * 60 * 1000,
  });
}

// Hover Prefetch
function ProductLink({ id }: { id: string }) {
  const qc = useQueryClient();
  return (
    <Link
      to={`/products/${id}`}
      onMouseEnter={() => qc.prefetchQuery({
        queryKey: productKeys.detail(id),
        queryFn: () => api.products.get(id),
      })}
    >{id}</Link>
  );
}

// Optimistic Mutation
const mutation = useMutation({
  mutationFn: api.products.update,
  onMutate: async (updated) => {
    await qc.cancelQueries({ queryKey: productKeys.detail(updated.id) });
    const prev = qc.getQueryData(productKeys.detail(updated.id));
    qc.setQueryData(productKeys.detail(updated.id), updated);
    return { prev };
  },
  onError: (_e, vars, ctx) => qc.setQueryData(productKeys.detail(vars.id), ctx?.prev),
  onSettled: (_d, _e, vars) => qc.invalidateQueries({ queryKey: productKeys.detail(vars.id) }),
});
```

## 6. 폼 — react-hook-form + Zod

```tsx
const schema = z.object({
  name: z.string().min(1).max(100),
  price: z.coerce.number().positive(),
  category: z.enum(['electronics', 'clothing']),
});
type FormData = z.infer<typeof schema>;  // 타입 수동 작성 금지

function ProductForm() {
  const { register, handleSubmit, formState: { errors } } = useForm<FormData>({
    resolver: zodResolver(schema),
  });
  return (
    <form onSubmit={handleSubmit(data => mutation.mutate(data))}>
      <input {...register('name')} />
      {errors.name && <span>{errors.name.message}</span>}
    </form>
  );
}
```

스키마는 `features/{domain}/` 내 schema 파일에 위치. `z.coerce` = 문자열 폼 입력 변환.

## 7. 디렉토리 구조 — Feature-scoped

```
src/
  features/
    products/
      api/            # Query hooks, API 호출
      components/     # Feature 전용 컴포넌트
      hooks/          # Feature 전용 hooks
      types/
      index.ts        # Public API (barrel)
  components/         # 공유 UI (Button, Modal)
  hooks/              # 공유 hooks (useDebounce)
  lib/                # 유틸리티 (queryClient, api instance)
```

**절대 규칙**: Feature 간 직접 import 금지. 공유 = `src/components` 또는 `src/hooks`로.

## 8. 성능

이 가이드는 **React Compiler 미사용 기준**. Compiler 도입 시 아래 메모이제이션 규칙 생략 가능.

적용 기준:
- `useMemo`: 측정 가능한 비용의 계산
- `useCallback`: 하위 memo 컴포넌트에 전달하는 함수
- `memo()`: 같은 props로 자주 리렌더링되는 컴포넌트

**먼저 컴포지션으로 해결** (상태 내리기, 콘텐츠 올리기). 메모이제이션은 최후 수단.

## 9. Props 패턴

```tsx
// 네이밍: on + 요소 + 이벤트 (props), handle + 요소 + 이벤트 (핸들러)
type Props = {
  onItemSelect: (id: string) => void;
  onClose: () => void;
};

// Discriminated Union — boolean soup 금지
type ButtonProps =
  | { variant: 'button'; onClick: () => void }
  | { variant: 'link'; href: string }
  | { variant: 'submit' };
```

## 10. Error Boundary + Suspense

```tsx
function ProductPage({ id }: { id: string }) {
  return (
    <div>
      <ErrorBoundary fallback={<p>상세 로드 실패</p>}>
        <Suspense fallback={<DetailSkeleton />}>
          <ProductDetail id={id} />
        </Suspense>
      </ErrorBoundary>
      <ErrorBoundary fallback={<p>리뷰 불가</p>}>
        <Suspense fallback={<ReviewsSkeleton />}>
          <ProductReviews id={id} />
        </Suspense>
      </ErrorBoundary>
    </div>
  );
}
```

**ErrorBoundary는 Suspense 바깥.** 섹션별 독립 실패. `react-error-boundary` 사용.

## Locked Date
2026-04-09
