from redisearch import Client, IndexDefinition, TextField, NumericField, TagField 

def load_data(redis_server, redis_port, redis_password):
   load_client = Client(
      'ShoppingCart-v1',
      host=redis_server,
      password=redis_password,
      port=redis_port
   )
   
   definition = IndexDefinition(
           prefix=['SHOPPING_CART:'],
           language='English',
           score_field='title',
           score=0.5
           )
   load_client.create_index(
           (
               TextField("cart_id", weight=5.0),
               TextField('session', sortable=True),
               TextField('product_name', sortable=True),
               NumericField('price', sortable=True),
               NumericField('quantity', sortable=True),
               NumericField('unit_price', sortable=True),
               NumericField('identity_score', sortable=True),
               NumericField('profile_score', sortable=True),
               NumericField('ai_score', sortable=True),
               ),        
       definition=definition)

   # Finally Create the alias
   load_client.aliasadd("ShoppingCart")