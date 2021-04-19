sequenceDiagram
autonumber
    Catalog->>CHECK-IDENTITY: XADD to stream
    IdentityService->>CHECK-IDENTITY: XREAD from stream
    IdentityService-->IdentityService: is Guest?
    IdentityService-->CART-ADD: It's a Guest
    CartService-->CART-ADD: XREAD
    CartService->>ShoppingCart: Submit
