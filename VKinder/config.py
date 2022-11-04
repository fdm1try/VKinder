import os

DB_NAME = os.getenv("DB_NAME") or "vkinder"
DB_LOGIN = os.getenv("DB_LOGIN") or "postgres"
DB_PASS = os.getenv("DB_PASS") or "postgres"

VK_APP_ID = os.getenv("VK_APP_ID")
VK_GROUP_ID = os.getenv("VK_GROUP_ID")
VK_GROUP_TOKEN = os.getenv("VK_GROUP_TOKEN")
