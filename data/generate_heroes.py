import requests
import json
from datetime import datetime

## ----------- Generate Heroes List ---------------
# To be replaced with "created" file

# Fetch active heroes
url = "http://assets.deadlock-api.com/v2/heroes?only_active=true"

response = requests.get(url)
response.raise_for_status() # Stops if something breaks

heroes = response.json() # Hero list

# Create local hero data file
data = {
   # file data
   "last_updated": datetime.utcnow().isoformat(),
   "total_heroes": len(heroes),

   # rich data
   "heroes": heroes,
   
   # hero fast lookup
   "hero_map": {hero["id"]: hero["name"] for hero in heroes},

   # internal development class_name
   "hero_class_map": {hero["id"]: hero["class_name"] for hero in heroes}
}

# create file with data
with open("heroes.json", "w", encoding="utf-8") as f:
   json.dump(data, f, indent=2, ensure_ascii=False)

print(f"✅ Saved {len(heroes)} active heroes to heroes.json")
print("   Last updated:", data["last_updated"])
print("   Example: hero_map[13] =", data["hero_map"].get(13, "Not found"))