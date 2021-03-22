import csv
import redis

def load_data(redis_server, redis_port, redis_password, data_path):
   load_client = redis.Redis(
      host=redis_server,
      password=redis_password,
      port=redis_port
   )

   with open(data_path, encoding='utf-8') as csv_file:
      csv_reader = csv.reader(csv_file, delimiter=',')
      line_count = 0
      for row in csv_reader:
         if line_count > 0:
            load_client.sadd("USER_LIST", row[0])
         line_count += 1