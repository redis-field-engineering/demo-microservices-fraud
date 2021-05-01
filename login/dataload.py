import csv
import redis

def load_data(redis_server, redis_port, redis_password, data_path):
   load_client = redis.Redis(
      host=redis_server,
      password=redis_password,
      port=redis_port
   )

   CATEGORIES = [
     "Apparel", "Automotive", "Baby", "Beauty", "Books", "Camera",
     "Digital_Ebook_Purchase", "Digital_Music_Purchase", "Digital_Software", "Digital_Video_Download", "Digital_Video_Games",
     "Electronics", "Furniture", "Gift_Card", "Grocery", "Health_Personal_Care", "Home_Entertainment",
     "Home_Improvement", "Home", "Jewelry", "Kitchen", "Lawn_and_Garden", "Luggage",
     "Major_Appliances", "Mobile_Apps", "Mobile_Electronics", "Musical_Instruments", "Music", "Office_Products",
     "Outdoors", "PC", "Personal_Care_Appliances", "Pet_Products", "Shoes", "Software", "Sports", "Tools", "Toys", "Video_DVD",
     "Video_Games", "Video", "Watches", "Wireless" ]


   with open(data_path, encoding='utf-8') as csv_file:
      csv_reader =  csv.DictReader(csv_file, delimiter=',')
      for row in csv_reader:
         load_client.sadd("USER_LIST", row['user'])
         for c in CATEGORIES:
            try:
               if int(row[c]) > 0:
                  load_client.execute_command('BF.ADD', "BFPROFILE:Category:{}".format(c), row['user'])
                  for z in row['levels'].split(":"):
                     load_client.execute_command('BF.ADD', "BFPROFILE:{}:{}".format(c, z), row['user'])
               load_client.hset(
                  "user:profile:{}".format(row['user']),
                  mapping={c: row[c]}
                  )
            except:
               x = 1
