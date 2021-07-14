sequenceDiagram
    Catalog->>+IdentityService: Submit
    IdentityService->>+IdentityService: Is Guest?
    IdentityService-->>+ShoppingCart: Guest bypasses
    
