# Kotlin Architecture Guide (LOCKED)

> 이 가이드가 존재하는 동안 아래 패턴에 반하는 대안을 검색하거나 제안하지 않는다.

## 1. Package Structure — Hexagonal

```
com.example.{domain}/
├── domain/
│   ├── model/          # Entity, Value Object, Domain Event
│   ├── port/
│   │   ├── inbound/    # UseCase 인터페이스
│   │   └── outbound/   # Repository, Gateway 인터페이스
│   └── exception/      # sealed error 계층
├── application/
│   └── usecase/        # UseCase 구현 (오케스트레이션)
├── adapter/
│   ├── inbound/web/    # Controller, Request/Response DTO
│   └── outbound/persistence/  # JPA Adapter, Entity, Mapper
└── config/             # DI, 프레임워크 설정
```

**규칙**: `domain`, `application`은 프레임워크 import 금지. `adapter`와 `config`만 Spring 의존.

## 2. UseCase 패턴

```kotlin
// Port (inbound) — fun interface
fun interface CreateOrderUseCase {
    suspend operator fun invoke(command: CreateOrderCommand): OrderResult
}

// Command — data class, 생성 시 검증
data class CreateOrderCommand(
    val customerId: CustomerId,
    val items: List<OrderItemCommand>,
) {
    init { require(items.isNotEmpty()) { "최소 1개 항목 필요" } }
}

// Result — sealed interface (예외 아님)
sealed interface OrderResult {
    data class Success(val orderId: OrderId) : OrderResult
    data class CustomerNotFound(val customerId: CustomerId) : OrderResult
}

// 구현
class CreateOrderUseCaseImpl(
    private val customers: CustomerRepository,
    private val orders: OrderRepository,
) : CreateOrderUseCase {
    override suspend fun invoke(command: CreateOrderCommand): OrderResult {
        val customer = customers.findById(command.customerId)
            ?: return OrderResult.CustomerNotFound(command.customerId)
        val order = Order.create(customer, command.items)
        orders.save(order)
        return OrderResult.Success(order.id)
    }
}
```

**핵심**: 예상 실패는 sealed 타입으로 반환. throw는 버그/인프라 에러만.

## 3. Port / Adapter 네이밍

```kotlin
// Port — 기능으로 명명 (기술명 X)
fun interface OrderRepository {
    suspend fun save(order: Order): Order
    suspend fun findById(id: OrderId): Order?
}

// Adapter — 기술로 명명
class OrderJpaAdapter(
    private val jpaRepo: OrderJpaRepository,
) : OrderRepository { ... }
```

## 4. Domain Model

```kotlin
// Value Object — @JvmInline value class
@JvmInline value class OrderId(val value: UUID) {
    companion object { fun generate() = OrderId(UUID.randomUUID()) }
}

@JvmInline value class Money(val cents: Long) {
    init { require(cents >= 0) }
    operator fun plus(other: Money) = Money(cents + other.cents)
}

// Entity — class (data class 아님). identity 기반 동등성.
class Order private constructor(
    val id: OrderId,
    val customerId: CustomerId,
    private val _items: MutableList<OrderItem>,
    var status: OrderStatus,
) {
    val items: List<OrderItem> get() = _items.toList()

    fun cancel() {
        check(status == OrderStatus.PLACED) { "PLACED만 취소 가능" }
        status = OrderStatus.CANCELLED
    }

    companion object {
        fun create(customer: Customer, items: List<OrderItemCommand>) =
            Order(OrderId.generate(), customer.id, items.map { it.toDomain() }.toMutableList(), OrderStatus.PLACED)
    }
}

// 도메인 에러 — sealed class
sealed class DomainError(val message: String) {
    class NotFound(val resource: String, val id: Any) : DomainError("$resource $id not found")
    class BusinessRule(reason: String) : DomainError(reason)
}
```

**규칙**: `data class` = VO/DTO, `class` = Entity, `@JvmInline value class` = 단일 필드 래퍼.

## 5. Controller — 매핑만

```kotlin
@RestController
@RequestMapping("/api/orders")
class OrderController(private val createOrder: CreateOrderUseCase) {

    @PostMapping
    suspend fun create(@RequestBody @Valid req: CreateOrderRequest): ResponseEntity<Any> =
        when (val result = createOrder(req.toCommand())) {
            is OrderResult.Success -> ResponseEntity.status(201).body(OrderResponse(result.orderId))
            is OrderResult.CustomerNotFound -> ResponseEntity.status(404).body(ErrorBody("CUSTOMER_NOT_FOUND"))
        }
}
```

**Controller 3원칙**: 역직렬화 → UseCase 호출 → 직렬화. 로직 금지.

## 6. 테스팅

```kotlin
// 네이밍: should [기대] when [조건]
// Fake > Mock (인메모리 구현)
class CreateOrderUseCaseTest {
    private val customers = InMemoryCustomerRepository()
    private val orders = InMemoryOrderRepository()
    private val sut = CreateOrderUseCaseImpl(customers, orders)

    @Test
    fun `should create order when customer exists`() = runTest {
        val customer = customers.save(aCustomer())
        val result = sut(aCreateOrderCommand(customerId = customer.id))
        assertThat(result).isInstanceOf<OrderResult.Success>()
    }
}

// 팩토리 함수 — 기본값 제공
fun aCustomer(id: CustomerId = CustomerId.generate(), name: String = "John") = Customer(id, name)
```

## 7. Coroutines

```kotlin
// suspend = I/O (DB, HTTP). Flow = 스트리밍.
// GlobalScope 금지. coroutineScope로 구조적 동시성.
suspend fun enrich(order: Order): EnrichedOrder = coroutineScope {
    val price = async { pricing.getPrice(order.id) }
    val stock = async { inventory.check(order.id) }
    EnrichedOrder(order, price.await(), stock.await())
}

// Adapter에서만 withContext(Dispatchers.IO)
class OrderJpaAdapter(private val jpa: OrderJpaRepository) : OrderRepository {
    override suspend fun findById(id: OrderId) = withContext(Dispatchers.IO) {
        jpa.findByIdOrNull(id.value)?.toDomain()
    }
}
```

## 8. 트랜잭션 경계

- `@Transactional`은 UseCase(Application 레이어)에 선언
- Adapter에는 `@Transactional` 금지 (UseCase가 트랜잭션 범위 결정)
- 읽기 전용: `@Transactional(readOnly = true)`

## 9. Null 처리

- `findById(): T?` = 부재가 정상
- `!!` 프로덕션 코드 금지
- `requireNotNull` / `checkNotNull`은 메시지와 함께
- nullable 보다 기본값 선호: `val apt: String = ""`

## 10. Extension Function

- DO: 도메인 변환 (`String.toOrderId()`, `OrderEntity.toDomain()`)
- DO: 같은 파일 내 유틸리티 (`internal fun Instant.isOlderThan()`)
- DON'T: 제네릭 타입에 범용 이름 (`List<T>.process()`)
- DON'T: 외부 상태 접근 (순수 함수 유지)

## Locked Date
2026-04-09
