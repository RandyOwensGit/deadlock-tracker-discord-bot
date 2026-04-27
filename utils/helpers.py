import datetime
from utils.heroes import HERO_MAP
from utils.api import get_match
from utils.friends import get_friend_name_by_steam_id, get_steam_id_by_deadlock_id

# ============================= HELPER FUNCTIONS =============================

## Convert seconds to HH:MM:SS or MM:SS format
def format_match_time_duration(seconds: int) -> str:
   time = ""

   if seconds >= 3600:
      time = "01"
   else:
      time += datetime.datetime.fromtimestamp(seconds).strftime('%M:%S')

   return time

## Formatted Match Line
# TODO - from DB?
def format_match_line(match: dict, steam_id: int) -> str:
      # Hero Name
   hero_name = HERO_MAP.get(str(match.get('hero_id')))

   # Result
   if match.get('match_result') == 0:
      result = "loss"
   else:
      result = "win"
   
   # KDA
   kills = match.get('player_kills', 0)
   deaths = match.get('player_deaths', 0)
   assists = match.get('player_assists', 0)
   kda = f"{kills}/{deaths}/{assists}"

   # Souls (net_worth)
   souls = match.get('net_worth', 0)
   souls_formatted = f"{souls:,}"

   # Duration
   duration_sec = match.get("match_duration_s")
   duration = format_match_time_duration(duration_sec)

   # Finding friends in match
   match_data = get_match(match.get('match_id'))
   match_info = match_data.get('match_info')
   players_in_match = match_info.get('players')

   # Getting Lane Partner
   assigned_lane = 0       # Assigned lane of calling player
   player_name = ""        #a Name of calling player
   assigned_team = None    # assigned team
   lane_partner = ""       # Correct Partner

   # Getting calling player's lane & name
   for player in players_in_match:
      player_id = get_steam_id_by_deadlock_id(int(player['account_id']))

      # Find caller by deadlock id in match
      if player_id == steam_id:
         # Get caller's lane
         assigned_lane = player['assigned_lane']

         # Set caller name
         player_name = get_friend_name_by_steam_id(player['account_id'])

         # Set caller team
         assigned_team = player['team']

         # done
         break

   # Finding lane partner
   for player in players_in_match:

      # found same lane as caller
      if assigned_lane == player['assigned_lane']:
         # Getting friend's name
         lane_partner = get_friend_name_by_steam_id(player['account_id'])

         # Check if lane_partner is caller = ignore
         if lane_partner == player_name:
            lane_partner = 'None'
            continue

         # Check if lane_partner is on the correct team
         if player['team'] != assigned_team:
            lane_partner = 'None'
            continue

         break

      # Random lane partner
      if lane_partner == 'None':
         lane_partner = 'Random'

   return f"{hero_name:<12} | {result:<4} | {kda:<8} | {souls_formatted:<7}souls | {duration} | Lane Partner: {lane_partner}"

