sequenceDiagram
autonumber
    Catalog->>CHECK-IDENTITY: XADD to stream
    IdentityService->>CHECK-IDENTITY: XREAD from stream
    IdentityService-->IdentityService: Score
    IdentityService-->CHECK-PROFILE: XADD to stream
    ProfileService-->CHECK-PROFILE: XREAD
    ProfileService->>ProfileService: Score
    ProfileService->>CHECK-AI: XADD to stream
    AIService-->CHECK-AI: XREAD
    AIService-->AIService: Score
    AIService->>CART-ADD: XADD
    CartService-->CART-ADD: XREAD
    CartService->>ShoppingCart: Submit
