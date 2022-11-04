import os
from dotenv import load_dotenv
load_dotenv()
DB_LOGIN, DB_PASS, COMMUNITY_TOKEN, USER_TOKEN = os.getenv('DB_LOGIN'), os.getenv('DB_PASS'), os.getenv('COMMUNITY_TOKEN'), os.getenv('USER_TOKEN')