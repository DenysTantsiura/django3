import configparser

from mongoengine import connect

from quotes.authentication import get_password


CONFIG_FILE = 'mongodatabase/config.ini'
MONGO_KEY = 'mongo_key.txt'  # to settings.py?

config = configparser.ConfigParser()
config.read(CONFIG_FILE)

mongo_user = config.get('DB_DEV', 'user')
# mongodb_pass = config.get('DB_DEV', 'password')
mongodb_pass = get_password(MONGO_KEY)
db_name = config.get('DB_DEV', 'db_name')
domain = config.get('DB_DEV', 'domain')

# connect to cluster on AtlasDB with connection string
connect(host=f"""mongodb+srv://{mongo_user}:{mongodb_pass}@{domain}/{db_name}?retryWrites=true&w=majority""", ssl=True)
