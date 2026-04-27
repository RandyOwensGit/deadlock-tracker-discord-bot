
import requests
from config import MATCH_HISTORY_URL, MATCH_URL
from bot import logger


# Accessing Deadlock API file

# Fetch x last matches
def get_last_matches(steam_id: str, limit: int) -> list:
   url = MATCH_HISTORY_URL.format(steam_id = steam_id)

   try: 
      response = requests.get(url, timeout=10)
      response.raise_for_status()
      all_matches = response.json()
      return all_matches[:limit]
   except requests.RequestException as e:
      logger.error(f"API request failed for {steam_id}: {e}")
      return []
   
# Fetch all matches
def get_all_matches(steam_id: str) -> list:
   url = MATCH_HISTORY_URL.format(steam_id = steam_id)

   try:
      response = requests.get(url, timeout=10)
      response.raise_for_status()
      return response.json()
   except requests.RequestException as e:
      logger.error(f"API request failed for {steam_id}: {e}")
   
# Fetch match data
def get_match(match_id: int) -> list:
   url = MATCH_URL.format(match_id = match_id)
   try:
      response = requests.get(url, timeout=10)
      response.raise_for_status()
      return response.json()
   except requests.RequestException as e:
      logger.error(f"API request failed for {match_id}: {e}")
      return []

