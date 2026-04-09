# TypeScript Architecture Guide (LOCKED)

> 이 가이드가 존재하는 동안 아래 패턴에 반하는 대안을 검색하거나 제안하지 않는다.

## 1. 타입 설계

```ts
// Discriminated Union > 넓은 인터페이스
type Result<T, E = Error> =
  | { ok: true; value: T }
  | { ok: false; error: E };

// Branded Type — 도메인 원시 타입
type UserId = string & { readonly __brand: unique symbol };
const UserId = (id: string): UserId => {
  if (!id.startsWith("usr_")) throw new Error("Invalid UserId");
  return id as UserId;
};

// satisfies — 타입 안전 + 좁은 추론 유지
const CONFIG = {
  maxRetries: 3,
  timeout: 5000,
} satisfies Record<string, number>;
```

## 2. 모듈 구성

```
src/
  features/
    user/
      user.schema.ts     # Zod 스키마 + 추론 타입
      user.service.ts     # 비즈니스 로직
      user.repository.ts  # 데이터 접근
      user.errors.ts      # 도메인 에러
      index.ts            # Public API만 export
  shared/
    result.ts
    branded.ts
```

Barrel export는 feature 경계에서만. feature 내부는 직접 import OK.

## 3. 에러 처리 — Result 패턴

```ts
// 예상 실패 = Result 반환. throw = 버그만.
function parseAge(input: string): Result<number, "NOT_A_NUMBER" | "OUT_OF_RANGE"> {
  const n = Number(input);
  if (Number.isNaN(n)) return { ok: false, error: "NOT_A_NUMBER" };
  if (n < 0 || n > 150) return { ok: false, error: "OUT_OF_RANGE" };
  return { ok: true, value: n };
}

// 소진적 에러 처리
const result = parseAge(input);
if (!result.ok) {
  switch (result.error) {
    case "NOT_A_NUMBER": break;
    case "OUT_OF_RANGE": break;
    // 누락 시 컴파일 에러
  }
}
```

## 4. Zod — 스키마가 타입의 원천

```ts
const UserSchema = z.object({
  id: z.string().brand<"UserId">(),
  email: z.string().email(),
  role: z.enum(["admin", "member"]),
  createdAt: z.coerce.date(),
});

type User = z.infer<typeof UserSchema>;  // 타입 수동 작성 금지

const CreateUserInput = UserSchema.omit({ id: true, createdAt: true });
type CreateUserInput = z.infer<typeof CreateUserInput>;
```

**규칙**: 경계에서 검증, 내부는 타입 신뢰.

## 5. Async

```ts
// 도메인 에러는 reject 아닌 Result로 반환
async function fetchUser(id: string): Promise<Result<User, "NOT_FOUND" | "NETWORK">> {
  try {
    const res = await fetch(`/api/users/${id}`);
    if (res.status === 404) return { ok: false, error: "NOT_FOUND" };
    return { ok: true, value: UserSchema.parse(await res.json()) };
  } catch {
    return { ok: false, error: "NETWORK" };
  }
}

// 병렬 + 부분 실패 = Promise.allSettled
const results = await Promise.allSettled(ids.map(fetchUser));
```

## 6. 불변성

```ts
// as const — 리터럴 튜플, 설정
const ROLES = ["admin", "member", "guest"] as const;
type Role = (typeof ROLES)[number];

// readonly — 함수 경계에서 "변경 안 함" 시그널
function processItems(items: readonly Item[]): Summary { ... }
```

## 7. 함수 설계

```ts
// 제네릭 제약 > 오버로드 (단순, 유지보수 용이)
function pick<T, K extends keyof T>(obj: T, keys: K[]): Pick<T, K> {
  return Object.fromEntries(keys.map(k => [k, obj[k]])) as Pick<T, K>;
}

// 오버로드는 반환 타입이 입력에 따라 다를 때만
```

## 8. Enum 대안

```ts
// TypeScript enum 금지 (런타임 오버헤드, tree-shaking 불가)
// const object + 유니온 타입 사용
const Status = {
  Pending: "pending",
  Active: "active",
  Disabled: "disabled",
} as const;

type Status = (typeof Status)[keyof typeof Status];
```

## 9. 테스팅 — Vitest

```ts
describe("createUser", () => {
  it("returns ok with valid input", async () => {
    const result = await createUser({ email: "a@b.com", role: "member" });
    expect(result.ok).toBe(true);
  });
});

// 타입 레벨 테스트
import { expectTypeOf } from "vitest";
it("infers User from schema", () => {
  expectTypeOf<User>().toHaveProperty("id");
});
```

## 10. API 레이어 — 타입 안전 Fetch

```ts
type ApiRoutes = {
  "GET /users": { response: User[]; query: { role?: Role } };
  "POST /users": { response: User; body: CreateUserInput };
};
```

라우트 맵 = API 형태의 단일 원천.

## 핵심 원칙

- **파생, 중복 금지** — 스키마/const에서 타입 추론
- **경계에서 검증, 내부는 신뢰** — parse at entry, trust inside
- **불법 상태 표현 불가** — discriminated union으로 무효 조합 차단
- **Result > throw** (예상 실패), **satisfies > annotation** (좁은 추론)

## Locked Date
2026-04-09
