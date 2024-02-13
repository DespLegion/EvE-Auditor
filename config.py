import os
from dotenv import load_dotenv

load_dotenv()

conf = {
    'token': os.getenv('TOKEN'),  # get bot token from https://discord.com/developers/applications/
    'bot': os.getenv('BOT_NAME'),  # get bot name from https://discord.com/developers/applications/
    'id': os.getenv('BOT_ID'),  # replace with bot id from https://discord.com/developers/applications/
    'prefix': os.getenv('BOT_PREFIX'),  # bot command prefix
}

dbconf = {
    'db_host': os.getenv('DB_HOST'),
    'db_port': int(os.getenv('DB_PORT')),
    'db_name': os.getenv('DB_NAME'),
    'db_user': os.getenv('DB_USER'),
    'db_pass': os.getenv('DB_PASS'),
}
