graph TD
    A[<font size=21 fa:fa-laptop] -->|http| Kong("<img src='https://apifriends.com/wp-content/uploads/2018/02/kong.png'; width='80' />")
    Kong -->|/catalog| CatalogService[fa:fa-server Catalog]
    Kong -->|/cart| CartService[fa:fa-server Cart]
    Kong -->|/login| LoginService[fa:fa-server Login]
    Kong -->|/logs| LogsService[fa:fa-server Logs]
    Redis("<img src='https://cdn.iconscout.com/icon/free/png-512/redis-83994.png'; width='80'  />")
    Gears("<img src='https://avatars.githubusercontent.com/u/48404293?s=400&v=4'; width='80' />")
    CatalogService -->|search| Redis
    CartService -->|AI/search| Redis
    LogsService --> Redis
    LoginService --> Redis
    Gears <--> Redis

{
  "theme": "dark",
  "securityLevel": "loose"
}
