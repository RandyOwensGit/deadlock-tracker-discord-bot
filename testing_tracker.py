import json
import requests
import datetime

# Load the heroes map quick access
with open("heroes.json", "r", encoding="utf-8") as f:
   hero_data = json.load(f)

HERO_MAP = hero_data["hero_map"]

# SteamID to use
# personal SteamID for now in this test environment
STEAMID = 76561198051933872

# Function to get entire match history 
def get_match_history():
   # Endpoint for match history
   url = f"https://api.deadlock-api.com/v1/players/{STEAMID}/match-history"
   response = requests.get(url)
   
   if response.status_code == 200:
      data = response.json()
      print("Last 5 matches: ")
      for match in data[:5]:
         matchId = match['match_id']
         matchTime = match['match_duration_s']
         heroName = HERO_MAP.get(str(match['hero_id']))
         result = match['match_result']

         # Formatting Time
         if matchTime >= 3600:
            time = "01:"
         else:
            time = ""

         time += datetime.datetime.fromtimestamp(matchTime).strftime('%M:%S')

         # Formatting Win/Loss
         if result == 0:
            result = "loss"
         else:
            result = "win"

         # Printing Match Data Line
         print(f"Match ID: {matchId} | Hero: {heroName} | Result: {result} | {time}")
      else:
         print("Error:" , response.status_code)

get_match_history()