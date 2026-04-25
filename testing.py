






import requests


# response = requests.get(f"https://api.deadlock-api.com/v1/players/76561198118775837/match-history")
# data = response.json()

# print(type(data))           # list or dict?
# print(data.keys() if isinstance(data, dict) else "It's a list!")
# if isinstance(data, dict):
#    print("Keys:", list(data.keys()))
#    print("Sample:", data.get("matches") or data.get("data") or data)

# match_id = data[0].get('match_id')

# print(f"\nMATCH-ID:::::::::::::::::: {match_id}\n")

# match_response = requests.get(f"https://api.deadlock-api.com/v1/matches/{data[0].get('match_id')}/metadata?is_custom=false")
# match_data = response.json()

# print(match_data)

   
matches = None

#Fetch ALL matches for a player from the Deadlock API
url = f"https://api.deadlock-api.com/v1/players/76561198118775837/match-history"
try:
   response = requests.get(url, timeout=15)
   response.raise_for_status()
   matches = response.json()

   # print(matches)
        
   if isinstance(matches, list):
      print(f"✅ Successfully fetched {len(matches)} matches")
   else:
      print(f"⚠️  Unexpected response format: {type(matches)}")
            
except Exception as e:
   print(f"❌ Error fetching matches for : {e}")

id = 76561198118775837

# Go through matches data
for match in matches:
   # Get the match data
   url = f"https://api.deadlock-api.com/v1/matches/{match.get('match_id')}/metadata?is_custom=false"
   match_response = requests.get(url, timeout=15)
   match_data = match_response.json()
   
   # Getting Data -> match_data['match_info'].get('x')

   print("-----------------------------------------------------------------------------------------------------------------------------")
   
   # Get the data we dont need from specific player:
   # match id, timestamp(start time), duration_s, mode, winning_team, 
   

   # Cycle through players until caller is found
   # account_id (convert to steam id?), team, kills, deaths, assists, net_worth, denies, last_hits, lane, creep_kills, 
   # player_damage, player_healing, max_health, shots_hit, shots_missed



# # Once you get the matches list
# # Need to go through each one individually
# url = f"https://api.deadlock-api.com/v1/matches/{matches.get('match_id')}/metadata?is_custom=false"
# match_response = requests.get(url, timeout=15)
# match_response.raise_for_status()
# match = match_response.json()
# print(type(match))
# print(match.keys() if isinstance(match, dict) else "It's a list!")
# match_info = match.get('match_info')

# print(f"MATCH INFO: {match_info}")

