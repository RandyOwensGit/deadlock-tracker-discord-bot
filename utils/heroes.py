import json
from pathlib import Path
from config import HEROES_JSON_PATH

HERO_MAP = {}
HERO_FULL = []

def load_heroes():
   # Load heroes from the JSON file
   global HERO_MAP, HERO_FULL

   try:
      path = Path(HEROES_JSON_PATH)
      if not path.exists():
         print(f"heroes.json not found at {HEROES_JSON_PATH}")
         return False
      
      with open(path, "r", encoding="utf-8") as f:
         hero_data = json.load(f)

      HERO_MAP = hero_data.get("hero_map", {})
      HERO_FULL = hero_data.get("heroes", [])

      print(f"Loaded {len(HERO_MAP)} heroes from {HEROES_JSON_PATH}")
      return True
   except Exception as e:
      print(f"Failed to load heroes: {e}")
      return False

load_heroes()

# Get hero name via hero_map
def get_hero_name(hero_id):
   if hero_id is None:
      return "Unknown Hero"
   return HERO_MAP.get(str(hero_id), HERO_MAP.get(hero_id, f"Unknown ({hero_id})"))