import datetime

import requests

matchTime = 3214

if matchTime >= 3600:
   time = "01:"
else:
   time = ""


time += datetime.datetime.fromtimestamp(matchTime).strftime('%M:%S')

print(time)


MATCH_HISTORY_URL = "https://api.deadlock-api.com/v1/players/{steam_id}/match-history"

# Fetch x last matches from Deadlock API
def get_last_matches(steam_id: str, limit: int) -> list:
   url = MATCH_HISTORY_URL.format(steam_id = steam_id)
   try:
      response = requests.get(url, timeout=10)
      response.raise_for_status()
      all_matches = response.json()
      return all_matches[:limit]
   except requests.RequestException as e:
      return []

data = get_last_matches(76561198051933872, 1)
account_id = data[0]['account_id']

print(account_id)












