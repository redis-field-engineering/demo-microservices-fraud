sequenceDiagram
    Catalog->>+IdentityService: Submit
    IdentityService->>+IdentityService: Score Identity
    IdentityService-->>+ProfileService: ID score 0.5
    ProfileService->>+ProfileService: Score Profile
    ProfileService->>+AIService: Profile score 0.0
    AIService->>+AIService: MBA Score
    AIService->>ShoppingCart: AI Score 0.01
