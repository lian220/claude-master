# Backend Architecture Patterns

## Table of Contents

1. [Spring Boot + Kotlin Hexagonal Architecture](#spring-boot--kotlin-hexagonal-architecture)
2. [Gradle Multi-Module 구조](#gradle-multi-module-구조)
3. [Python FastAPI Clean Architecture](#python-fastapi-clean-architecture)
4. [Port/Adapter 네이밍 표준](#portadapter-네이밍-표준)

---

## Spring Boot + Kotlin Hexagonal Architecture

참조: [hex-arch-kotlin-spring-boot](https://github.com/nicusX/hex-arch-kotlin-spring-boot)

### 단일 모듈 구조

```
src/main/kotlin/com/example/app/
├── domain/
│   ├── {aggregate}/
│   │   ├── entity/           # 도메인 엔티티 (순수 Kotlin, 프레임워크 무관)
│   │   ├── vo/               # Value Objects (불변, 유효성 검증 포함)
│   │   ├── event/            # 도메인 이벤트
│   │   ├── exception/        # 도메인 예외
│   │   ├── port/
│   │   │   ├── inbound/      # UseCase 인터페이스 (Primary Port)
│   │   │   └── outbound/     # Repository/External Port (Secondary Port)
│   │   └── service/          # 도메인 서비스 (복수 엔티티 로직)
│   └── shared/               # 공유 도메인 객체 (공통 VO 등)
├── application/
│   ├── {aggregate}/          # UseCase 구현 (@Service)
│   └── shared/               # 공통 Application 서비스
├── infrastructure/
│   ├── config/               # Spring 설정 (@Configuration)
│   ├── persistence/
│   │   ├── entity/           # JPA 엔티티 (@Entity)
│   │   ├── repository/       # Spring Data JPA Repository
│   │   └── mapper/           # Domain <-> JPA 매퍼
│   ├── external/             # 외부 API 클라이언트 (Adapter)
│   ├── messaging/            # 메시징 (Kafka, RabbitMQ)
│   └── security/             # Spring Security 설정
└── presentation/
    ├── rest/
    │   ├── {aggregate}/      # REST Controller
    │   ├── dto/              # Request/Response DTO
    │   └── mapper/           # DTO <-> Command/Query 매퍼
    ├── advice/               # @RestControllerAdvice (전역 예외 처리)
    └── filter/               # HTTP 필터
```

### 의존성 규칙

```
Presentation → Application → Domain ← Infrastructure
     ↓              ↓           ↑            ↑
  Controller     UseCase     Entity      Adapter
   (REST)      (@Service)   (Pure)     (JPA, API)
```

- Domain 레이어: 프레임워크 어노테이션 금지 (`@Service`, `@Component`, `@Entity` 금지)
- Application 레이어: Domain Port만 의존, Infrastructure 직접 참조 금지
- Infrastructure 레이어: Domain Outbound Port를 구현 (Adapter 패턴)
- Presentation 레이어: Application UseCase만 의존

### 핵심 코드 패턴

#### Domain Entity

```kotlin
// domain/order/entity/Order.kt
class Order private constructor(
    val id: OrderId,
    val items: List<OrderItem>,
    val status: OrderStatus,
    val totalAmount: Money
) {
    companion object {
        fun create(items: List<OrderItem>): Order {
            require(items.isNotEmpty()) { "주문 항목은 최소 1개 이상" }
            return Order(
                id = OrderId.generate(),
                items = items,
                status = OrderStatus.CREATED,
                totalAmount = items.sumOf { it.price }
            )
        }
    }

    fun confirm(): Order = copy(status = OrderStatus.CONFIRMED)
}
```

#### Inbound Port (UseCase Interface)

```kotlin
// domain/order/port/inbound/CreateOrderUseCase.kt
interface CreateOrderUseCase {
    fun execute(command: CreateOrderCommand): Order
}

data class CreateOrderCommand(
    val userId: UserId,
    val items: List<OrderItemCommand>
)
```

#### Outbound Port

```kotlin
// domain/order/port/outbound/OrderRepositoryPort.kt
interface OrderRepositoryPort {
    fun save(order: Order): Order
    fun findById(id: OrderId): Order?
    fun findByUserId(userId: UserId): List<Order>
}
```

#### Application UseCase

```kotlin
// application/order/CreateOrderUseCaseImpl.kt
@Service
class CreateOrderUseCaseImpl(
    private val orderRepository: OrderRepositoryPort,
    private val eventPublisher: DomainEventPublisher
) : CreateOrderUseCase {

    @Transactional
    override fun execute(command: CreateOrderCommand): Order {
        val items = command.items.map { it.toDomain() }
        val order = Order.create(items)
        val saved = orderRepository.save(order)
        eventPublisher.publish(OrderCreatedEvent(saved.id))
        return saved
    }
}
```

---

## Gradle Multi-Module 구조

### 표준 멀티모듈 레이아웃

```
project-root/
├── build.gradle.kts          # 루트 빌드 (공통 플러그인, 의존성)
├── settings.gradle.kts       # 모듈 등록
├── gradle/
│   └── libs.versions.toml    # Version Catalog
├── buildSrc/                 # 커스텀 플러그인/컨벤션
│   └── src/main/kotlin/
│       └── conventions/
│           ├── kotlin-conventions.gradle.kts
│           └── spring-conventions.gradle.kts
├── core-domain/              # 순수 도메인 (프레임워크 무관)
│   ├── build.gradle.kts
│   └── src/
├── core-application/         # 유스케이스 (도메인만 의존)
│   ├── build.gradle.kts
│   └── src/
├── infra-persistence/        # JPA 어댑터
│   ├── build.gradle.kts
│   └── src/
├── infra-external/           # 외부 API 어댑터
│   ├── build.gradle.kts
│   └── src/
├── api-rest/                 # REST API (Presentation)
│   ├── build.gradle.kts
│   └── src/
└── app-bootstrap/            # 부트스트랩 (main, 설정 통합)
    ├── build.gradle.kts
    └── src/
```

### settings.gradle.kts

```kotlin
rootProject.name = "my-project"

include(
    "core-domain",
    "core-application",
    "infra-persistence",
    "infra-external",
    "api-rest",
    "app-bootstrap"
)
```

### 모듈 간 의존성

```kotlin
// core-application/build.gradle.kts
dependencies {
    implementation(project(":core-domain"))
}

// infra-persistence/build.gradle.kts
dependencies {
    implementation(project(":core-domain"))
    implementation(project(":core-application"))
}

// app-bootstrap/build.gradle.kts
dependencies {
    implementation(project(":core-domain"))
    implementation(project(":core-application"))
    implementation(project(":infra-persistence"))
    implementation(project(":infra-external"))
    implementation(project(":api-rest"))
}
```

### Version Catalog (gradle/libs.versions.toml)

```toml
[versions]
kotlin = "1.9.25"
spring-boot = "3.4.1"
jvm-target = "21"

[libraries]
spring-boot-starter-web = { module = "org.springframework.boot:spring-boot-starter-web" }
spring-boot-starter-data-jpa = { module = "org.springframework.boot:spring-boot-starter-data-jpa" }
spring-boot-starter-test = { module = "org.springframework.boot:spring-boot-starter-test" }

[plugins]
kotlin-jvm = { id = "org.jetbrains.kotlin.jvm", version.ref = "kotlin" }
kotlin-spring = { id = "org.jetbrains.kotlin.plugin.spring", version.ref = "kotlin" }
spring-boot = { id = "org.springframework.boot", version.ref = "spring-boot" }
```

---

## Python FastAPI Clean Architecture

### 프로젝트 구조

```
src/
├── domain/
│   ├── {aggregate}/
│   │   ├── entity.py         # 도메인 엔티티 (Pydantic BaseModel)
│   │   ├── value_objects.py  # Value Objects
│   │   ├── repository.py     # Repository Protocol (ABC)
│   │   ├── service.py        # 도메인 서비스
│   │   └── exceptions.py     # 도메인 예외
│   └── shared/
│       └── base.py           # 공통 베이스 클래스
├── application/
│   ├── {aggregate}/
│   │   ├── commands.py       # Command DTO
│   │   ├── queries.py        # Query DTO
│   │   └── use_cases.py      # UseCase 구현
│   └── shared/
│       └── unit_of_work.py   # UoW 인터페이스
├── infrastructure/
│   ├── database/
│   │   ├── models.py         # SQLAlchemy Models
│   │   ├── repository.py     # Repository 구현
│   │   └── session.py        # DB 세션 관리
│   ├── external/             # 외부 API 클라이언트
│   └── config.py             # 환경 설정
├── presentation/
│   ├── api/
│   │   ├── v1/
│   │   │   ├── {aggregate}.py  # Router
│   │   │   └── schemas.py      # Request/Response 스키마
│   │   └── deps.py             # FastAPI Dependencies
│   └── middleware/
├── main.py                   # FastAPI app 초기화
└── container.py              # DI 컨테이너 (dependency-injector)
```

---

## Port/Adapter 네이밍 표준

### Port 네이밍

| 유형 | 패턴 | 예시 |
|------|------|------|
| Inbound Port | `{Action}{Aggregate}UseCase` | `CreateOrderUseCase` |
| Outbound Port (저장소) | `{Aggregate}RepositoryPort` | `OrderRepositoryPort` |
| Outbound Port (외부) | `{Service}Port` | `PaymentGatewayPort` |
| Outbound Port (메시징) | `{Event}PublisherPort` | `OrderEventPublisherPort` |

### Adapter 네이밍

| 유형 | 패턴 | 예시 |
|------|------|------|
| JPA Adapter | `Jpa{Aggregate}Repository` | `JpaOrderRepository` |
| API Adapter | `{Provider}{Service}Adapter` | `StripePaymentAdapter` |
| Messaging Adapter | `Kafka{Event}Publisher` | `KafkaOrderEventPublisher` |

### Command/Query 네이밍

| 유형 | 패턴 | 예시 |
|------|------|------|
| Command | `{Action}{Aggregate}Command` | `CreateOrderCommand` |
| Query | `{Action}{Aggregate}Query` | `FindOrderByIdQuery` |
| Event | `{Aggregate}{Action}Event` | `OrderCreatedEvent` |
