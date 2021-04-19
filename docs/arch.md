classDiagram
class Catalog
Catalog --|> RedisStreams
class RedisStreams{
        IDENTITY
        PROFILE
        AI
        CART
}
Identity Service <|-- RedisStreams : Read 
class Identity Service{
       Check IP
       Check Browser
}
Profile Service --|> RedisStreams : Write 

Profile Service <|-- RedisStreams : Read 
class Profile Service{
       Check Purchases
}
Identity Service --|> RedisStreams : Write 

Cart <|-- RedisStreams: Read
Cart --|> Redisearch: Write

AI Service <|-- RedisStreams : Read 
class AI Service{
       Check Purchases
}
AI Service --|> RedisStreams : Write 


