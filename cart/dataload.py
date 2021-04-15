from redisearch import Client, IndexDefinition, TextField, NumericField, TagField 
import redis
import re


def cart_score(redis_server, redis_port, redis_password, sessionid):
   c = redis.Redis(
   host=redis_server,
   password=redis_password,
   port=redis_port
   )

   try:
      tginfo = c.execute_command('RG.TRIGGER  score {}'.format(sessionid.replace("_", "")))[0].decode('utf-8')
      match = re.findall(r'\((\d{1,4}), (\d{1,4})\)', tginfo)
      if match:
         return(match[0])
      else:
         return((0, 0))
   except:
      return((0, 0))



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
