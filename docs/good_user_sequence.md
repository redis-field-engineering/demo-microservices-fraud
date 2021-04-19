sequenceDiagram
autonumber
    Catalog->>CHECK-IDENTITY: XADD to stream
    IdentityService->>CHECK-IDENTITY: XREAD from stream
    IdentityService-->IdentityService: Score
    IdentityService-->CHECK-PROFILE: XADD to stream
    ProfileService-->CHECK-PROFILE: XREAD
    ProfileService->>ProfileService: Score
    ProfileService->>CART-ADD: ID and Profile good!!
    CartService-->CART-ADD: XREAD
    CartService->>ShoppingCart: Submit

