# Kotlin + Spring Boot 구현 세부 가이드

> **상위 규범은 [kotlin.md](kotlin.md)다.** 이 문서는 kotlin.md가 다루지 않는 Spring Boot
> 어댑터 구현 세부(REST 표준, JPA, 에러 응답)만 보완한다. 두 문서가 충돌하면 무조건
> kotlin.md를 따른다. 패키지 구조·UseCase 형태·실패 표현(sealed Result)·테스트 대역
> (Fake > Mock)·트랜잭션 경계는 전부 kotlin.md에 있다.
>
> (구 spring-boot-expert 스킬에서 흡수. 원본은 kotlin.md와 패키지 구조·예외 기반 실패
> 표현이 충돌해 폐기했다.)

## 1. REST API 표준 — `adapter/inbound/web`

### URL 네이밍
- 복수형 명사: `/v1/orders`, `/v1/customers`
- 케밥 케이스: `/v1/order-items`
- 버전 접두사: `/v1/...`
- 동사 사용 금지: ~~`/getOrders`~~ → `/orders`

### HTTP 메서드
| 메서드 | 용도 | 응답 코드 |
|--------|------|-----------|
| GET | 조회 | 200 OK |
| POST | 생성 | 201 Created |
| PUT | 전체 수정 | 200 OK |
| PATCH | 부분 수정 | 200 OK |
| DELETE | 삭제 | 204 No Content |

### 요청/응답 DTO
Controller는 매핑만 한다(kotlin.md §5). DTO는 도메인 모델과 분리한다.

```kotlin
// Request DTO — Bean Validation 은 입력 형식 검증까지만.
// 도메인 불변식 검증은 Command init 블록의 몫이다 (kotlin.md §2)
data class CreateOrderRequest(
    @field:NotBlank val customerId: String,
    @field:Size(min = 1) val items: List<OrderItemRequest>,
)

// Response DTO — 도메인 모델을 직접 노출하지 않는다
data class OrderResponse(
    val id: String,
    val items: List<OrderItemResponse>,
    val createdAt: String,
)
```

### 페이징
```kotlin
@GetMapping
suspend fun list(
    @RequestParam(defaultValue = "0") page: Int,
    @RequestParam(defaultValue = "20") size: Int,
): PageResponse<OrderResponse> { ... }

data class PageResponse<T>(
    val content: List<T>,
    val page: Int,
    val size: Int,
    val totalElements: Long,
    val totalPages: Int,
)
```

## 2. 에러 응답 — sealed Result가 1차, 핸들러는 최후 방어선

kotlin.md §2가 규범이다: **예상 실패는 sealed Result로 반환하고, throw는 버그/인프라
에러만.** 따라서 Controller가 Result 분기를 HTTP 응답으로 매핑하는 것이 1차 경로다.

```kotlin
@PostMapping
suspend fun create(@Valid @RequestBody req: CreateOrderRequest): ResponseEntity<Any> =
    when (val result = createOrder(req.toCommand())) {
        is OrderResult.Success ->
            ResponseEntity.status(201).body(OrderResponse.from(result))
        is OrderResult.CustomerNotFound ->
            ResponseEntity.status(404).body(ErrorResponse.notFound("customer", result.customerId))
    }
```

`@RestControllerAdvice`는 **Result로 표현되지 않는 것만** 잡는다:
- `MethodArgumentNotValidException` — Bean Validation 실패 → 400 + 필드 상세
- 그 외 미처리 예외(버그/인프라) — → 500, 내부 메시지 노출 금지

```kotlin
data class ErrorResponse(
    val status: Int,
    val error: String,          // BAD_REQUEST / NOT_FOUND / INTERNAL_ERROR ...
    val message: String?,
    val details: List<FieldError>? = null,
    val timestamp: String = Instant.now().toString(),
)

data class FieldError(val field: String, val message: String)
```

에러 JSON 형식은 위 구조로 통일한다. 도메인 계층에 HTTP 상태 코드를 알게 하지 않는다.

## 3. JPA — `adapter/outbound/persistence`

### 도메인 모델과 JPA 엔티티 분리
- 도메인 모델: 순수 Kotlin, 프레임워크 의존 없음 (kotlin.md §4)
- JPA 엔티티: `@Entity` 등 어노테이션 사용, adapter 내부에만 존재
- 변환은 Mapper 확장 함수: `OrderEntity.toDomain()`, `Order.toEntity()` (kotlin.md §10)

```kotlin
@Entity
@Table(name = "orders")
class OrderEntity(
    @Id @Column(columnDefinition = "uuid")
    val id: UUID,

    @Column(nullable = false)
    val customerId: UUID,

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    val status: String,

    @Column(nullable = false, updatable = false)
    val createdAt: Instant,

    @OneToMany(mappedBy = "order", cascade = [CascadeType.ALL], orphanRemoval = true)
    val items: MutableList<OrderItemEntity> = mutableListOf(),
)
```

### Adapter 형태
Port는 기능으로, Adapter는 기술로 명명한다 (kotlin.md §3).

```kotlin
interface OrderJpaRepository : JpaRepository<OrderEntity, UUID> {
    fun findByCustomerId(customerId: UUID): List<OrderEntity>
}

class OrderJpaAdapter(
    private val jpaRepo: OrderJpaRepository,
) : OrderRepository {
    override suspend fun save(order: Order): Order =
        jpaRepo.save(order.toEntity()).toDomain()

    override suspend fun findById(id: OrderId): Order? =
        jpaRepo.findByIdOrNull(id.value)?.toDomain()
}
```

### N+1 방지
```kotlin
// FETCH JOIN
@Query("SELECT o FROM OrderEntity o JOIN FETCH o.items WHERE o.id = :id")
fun findByIdWithItems(@Param("id") id: UUID): OrderEntity?

// @EntityGraph
@EntityGraph(attributePaths = ["items"])
fun findByCustomerId(customerId: UUID): List<OrderEntity>
```

### 트랜잭션
kotlin.md §8 그대로: `@Transactional`은 UseCase에만, Adapter 금지, 읽기 전용은
`@Transactional(readOnly = true)`.
