






import requests


# response = requests.get(f"https://api.deadlock-api.com/v1/players/76561198118775837/match-history")
# data = response.json()

# print(type(data))           # list or dict?
# print(data.keys() if isinstance(data, dict) else "It's a list!")
# if isinstance(data, dict):
#    print("Keys:", list(data.keys()))
#    print("Sample:", data.get("matches") or data.get("data") or data)
   
# Here
"""Fetch ALL matches for a player from the Deadlock API."""
url = f"https://api.deadlock-api.com/v1/players/76561198118775837/match-history"
try:
   response = requests.get(url, timeout=15)
   response.raise_for_status()
   matches = response.json()
        
   if isinstance(matches, list):
      print(f"✅ Successfully fetched {len(matches)} matches")
   else:
      print(f"⚠️  Unexpected response format: {type(matches)}")
            
except Exception as e:
   print(f"❌ Error fetching matches for : {e}")

for match in matches:
   print(match['match_id'])


