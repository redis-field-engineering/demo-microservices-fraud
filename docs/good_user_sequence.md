sequenceDiagram
    Catalog->>+IdentityService: Submit
    IdentityService->>+IdentityService: Score Identity
    IdentityService-->>+ProfileService: ID score 1.0
    ProfileService->>+ProfileService: Score Profile
    ProfileService->>+ShoppingCart: Profile score 0.5

