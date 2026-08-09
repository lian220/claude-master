# Python Architecture Guide (LOCKED)

> 이 가이드가 존재하는 동안 아래 패턴에 반하는 대안을 검색하거나 제안하지 않는다.

## 1. 프로젝트 구조 — src Layout

```
myproject/
  pyproject.toml          # PEP 621 — 유일한 설정 파일
  src/
    myapp/
      domain/             # Entity, Value Object, 비즈니스 규칙
        models.py
        errors.py
      service/            # UseCase / 애플리케이션 로직
      repository/
        protocols.py      # Protocol 정의 (인터페이스)
        postgres.py       # 구현체
      api/                # 인바운드 어댑터 (HTTP, CLI)
        routes.py
        schemas.py        # Pydantic request/response
      infra/              # 아웃바운드 어댑터 (이메일, 큐)
  tests/
    conftest.py
```

도메인 경계별 패키지 구성. 파일 타입별 구성 금지.

## 2. 타입 힌트

**필수**: 함수 시그니처 (파라미터 + 반환), 클래스 속성, public API
**생략 가능**: 자명한 로컬 변수, 컴프리헨션, 테스트 본문

```python
# PEP 695 — Python 3.12+ 제네릭 문법
type Result[T] = T | AppError

def find[T](items: list[T], pred: Callable[[T], bool]) -> T | None:
    return next((x for x in items if pred(x)), None)
```

## 3. Pydantic — 경계에서만

```python
from pydantic import BaseModel, Field, field_validator

class CreateUserRequest(BaseModel):
    """인바운드 DTO — 신뢰할 수 없는 입력 검증"""
    email: str = Field(max_length=255)
    name: str = Field(min_length=1, max_length=100)

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        if "@" not in v:
            raise ValueError("invalid email")
        return v.lower()

class UserResponse(BaseModel):
    """아웃바운드 DTO — 직렬화 전용"""
    model_config = {"from_attributes": True}
    id: int
    email: str
```

**규칙**: Pydantic = 경계(API I/O, 설정), dataclass = 도메인 내부.

## 4. 에러 처리

```python
# 도메인 에러 계층
class AppError(Exception):
    def __init__(self, message: str, code: str = "UNKNOWN"):
        self.message = message
        self.code = code

class NotFoundError(AppError):
    def __init__(self, entity: str, id: object):
        super().__init__(f"{entity} {id} not found", code="NOT_FOUND")

# 예상 실패는 Result 패턴
@dataclass(frozen=True, slots=True)
class Ok[T]:
    value: T

@dataclass(frozen=True, slots=True)
class Err:
    error: AppError

type Result[T] = Ok[T] | Err

# 사용
match parse_age(user_input):
    case Ok(age): print(age)
    case Err(e): log.warning(e.message)
```

## 5. Async — TaskGroup (구조적 동시성)

```python
async def fetch_dashboard(user_id: int) -> Dashboard:
    async with asyncio.TaskGroup() as tg:
        profile = tg.create_task(fetch_profile(user_id))
        orders = tg.create_task(fetch_orders(user_id))
    return Dashboard(profile=profile.result(), orders=orders.result())
```

- `asyncio.TaskGroup` 사용 (`gather` 대신). 하나 실패 시 전체 취소.
- async = I/O 바운드만. CPU 바운드 = `ProcessPoolExecutor`.
- `except*`로 `ExceptionGroup` 처리.

## 6. 의존성 주입 — Protocol + 생성자

```python
from typing import Protocol

class UserRepository(Protocol):
    async def get(self, user_id: int) -> User | None: ...
    async def save(self, user: User) -> User: ...

class UserService:
    def __init__(self, repo: UserRepository, email: EmailSender) -> None:
        self._repo = repo
        self._email = email

# Composition root에서 조립
def create_app() -> App:
    repo = PostgresUserRepository(db)
    email = SmtpEmailSender(SMTP_HOST)
    service = UserService(repo, email)
    return App(service=service)
```

DI 프레임워크 불필요. Protocol + 생성자 주입으로 충분.

## 7. 테스팅 — pytest

```python
# Fake > Mock (인메모리 구현)
@pytest.fixture
def fake_repo() -> FakeUserRepository:
    return FakeUserRepository()

@pytest.fixture
def service(fake_repo) -> UserService:
    return UserService(repo=fake_repo, email=FakeEmailSender())

async def test_register_creates_user(service):
    user = await service.register(CreateUserRequest(email="a@b.com", name="A"))
    assert user.email == "a@b.com"

# parametrize로 엣지 케이스
@pytest.mark.parametrize("email,valid", [
    ("user@example.com", True),
    ("bad", False),
    ("", False),
])
def test_email_validation(email, valid):
    if valid:
        CreateUserRequest(email=email, name="X")
    else:
        with pytest.raises(Exception):
            CreateUserRequest(email=email, name="X")
```

`pytest-asyncio` + `mode = "auto"`. 파일명 `test_*.py`.

## 8. Dataclass vs Pydantic vs Attrs

| 용도 | 선택 |
|------|------|
| API 경계 (입출력, 설정) | **Pydantic** |
| 도메인 엔티티, VO | **dataclass** (frozen=True, slots=True) |
| 성능 민감 내부 | **attrs** (slots=True) |

## 9. 모듈 캡슐화

```python
# __init__.py에서 public API 선언
from myapp.domain.models import User, Order
__all__ = ["User", "Order"]
```

- `__all__` 필수. `_` 접두사 = private. 외부에서 `_private` 모듈 import 금지.

## Locked Date
2026-04-09
