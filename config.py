import os
from dotenv import load_dotenv

load_dotenv() # environment variables loaded

# Bot Config
BOT_TOKEN = os.getenv("BOT_TOKEN")
DEFAULT_STEAMID = os.getenv("DEFAULT_STEAMID")

# Paths
HEROES_JSON_PATH = "data/heroes.json"
DATABASE_PATH = "deadlock.db"

# Discord Settings
COMMAND_PREFIX = "!"

# API settings
MATCH_HISTORY_URL = "https://api.deadlock-api.com/v1/players/{steam_id}/match-history"
MATCH_URL = "https://api.deadlock-api.com/v1/matches/{match_id}/metadata?is_custom=false"