from redisearch import AutoCompleter, Client, IndexDefinition, TextField, NumericField, TagField, Suggestion
import random
import redis
import re


LEVELS = {
   'budget': {'min': 100, 'max': 1999},
   'bargain': {'min': 2000, 'max': 4999},
   'standard': {'min': 5000, 'max': 9999},
   'premium': {'min': 10000, 'max': 19999},
   'luxury': {'min': 20000, 'max': 99999},
}

def cart_score(redis_server, redis_port, redis_password, sessionid):
   c = redis.Redis(
   host=redis_server,
   password=redis_password,
   port=redis_port
   )

   try:
      if int(c.exists("CART_SCORE:{}".format(sessionid.replace("_", "")))) > 0:
         sc = c.hgetall("CART_SCORE:{}".format(sessionid.replace("_", "")))
         print(sc)
         return((sc[b'items'].decode('utf-8'), max([0, float(sc[b'score'].decode('utf-8'))])))
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
      'Catalog-v1',
      host=redis_server,
      password=redis_password,
      port=redis_port
   )
   load_ac = AutoCompleter(
   'categories:ac',
   conn = load_client.redis
   )
   
   definition = IndexDefinition(
           prefix=['catalog:'],
           language='English',
           score_field='title',
           score=0.5
           )
   load_client.create_index(
           (
               TextField("product", weight=5.0),
               NumericField("product_id", sortable=True),
               TextField('category', sortable=True),
               NumericField('price', sortable=True),
               TextField('level', sortable=True),
               ),        
       definition=definition)

   with open("./catagories.txt") as fp:
      counter = 199 
      lines = fp.readlines()
      for line in lines:
         load_ac.add_suggestions(Suggestion(line.rstrip(),  1.0))
         for level in LEVELS.keys():
            for i in range(3):
               counter += 1
               load_client.redis.hset(
                  "catalog:%s:%s:%d" %(line.rstrip(), level, i),
                  mapping = {
                     'product': "%s %s %d" %(line.rstrip(), level, i),
                     'product_id': counter,
                     'level': level,
                     'category': line.rstrip(),
                     'price': random.randint(LEVELS[level]['min'], LEVELS[level]['max'])/100
                  })

   # Finally Create the alias
   load_client.aliasadd("Catalog")
