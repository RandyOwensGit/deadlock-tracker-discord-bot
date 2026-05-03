from sqlalchemy import desc
from sqlalchemy.orm import joinedload
from database import Match, Player, PlayerMatch, PlayerRecord, Session
from bot import logger

""" Functions related to accessing the Database """

# Creating new record for players table
# Return 0 for success, 1 for already exists, 2 for error adding to DB
def create_player(steam_id: int, discord_id: int, deadlock_api_id: int, display_name: str) -> int :
   session = Session()

   try:
      # Check if player already exists
      existing = session.query(Player).filter_by(steam_id=steam_id).first()

      if existing:
         logger.info(f"Player: {steam_id} already exists in players table.")
         return 1
      
      # Create new player
      new_player = Player(
         steam_id=steam_id,
         discord_id=discord_id,
         deadlock_api_id=deadlock_api_id,
         display_name=display_name
      )

      session.add(new_player)
      session.commit()

      logger.info(f"New Player: {steam_id} added to players table.")
      return 0

   except Exception as e:
      session.rollback()
      logger.error(f"DB - Error adding player to players table: {e}")
      return 2
   finally:
      session.close()

# Creating new record for matches table from JSON
# Return 0 for success, 1 for already exists, 2 for error adding to DB
def create_match(session, data) -> int:

   # check if Match already exists
   existing = session.query(Match).filter_by(match_id=data.get('match_id')).first()

   if existing:
      logger.info(f"Match: {data.get('match_id')} already exists in matches table.")
      return 1
      
   new_match = Match(
      match_id=data.get('match_id'),
      timestamp=data.get('start_time'),
      duration_s=data.get('match_duration_s'),
      mode=data.get('match_mode'),
      winning_team=data.get('match_result')
   )

   session.add(new_match)

   logger.info(f"DB ADD---MatchID: {data.get('match_id')} added to matches table. (Pre-Commit)")

   return 0

# creating new record for player_matches table JSON
# When match has salts data
def create_player_match_with_salts(session, data, steam_id, match_id):

   # Check if player has already had their match statistics added for this match
   existing = session.query(PlayerMatch).filter_by(
      match_id=match_id,
      steam_id=steam_id
   ).first()

   if existing:
      logger.info(f"MatchID: {data.get('match_id')} & PlayerID: {id} data have already been added to the PlayerMatch table.")
      return 
      
   # Sub list need final index
   lastIndex = len(data.get('stats'))

   new_player_match = PlayerMatch(
      match_id=match_id,
      steam_id=steam_id,
      hero_id=data.get('hero_id'),
      team=data.get('team'),
      kills=data.get('kills'),
      deaths=data.get('deaths'),
      assists=data.get('assists'),
      net_worth=data.get('net_worth'),
      denies=data.get('denies'),
      last_hits=data.get('last_hits'),
      lane=data.get('assigned_lane'),
      creep_kills=data.get('stats')[lastIndex - 1].get('creep_kills'),
      player_damage=data.get('stats')[lastIndex - 1].get('player_damage'),
      player_healing=data.get('stats')[lastIndex - 1].get('player_healing'),
      max_health=data.get('stats')[lastIndex - 1].get('max_health'),
      shots_hit=data.get('stats')[lastIndex - 1].get('shots_hit'),
      shots_missed=data.get('stats')[lastIndex - 1].get('shots_missed'),
      is_complete=True 
   )

   session.add(new_player_match)

   logger.info(f"DB ADD---MatchID: {match_id} & PlayerID: {steam_id} added to player_matches table. (Pre-Commit)")
   return new_player_match

# creating new record for player_matches table JSON
# when match has NO SALTS
def create_player_match_without_salts(session, data, steam_id):

   # Check if player has already had their match statistics added for this match
   existing = session.query(PlayerMatch).filter_by(
      match_id=data.get('match_id'),
      steam_id=steam_id
   ).first()

   if existing:
      logger.info(f"MatchID: {data.get('match_id')} & PlayerID: {id} data have already been added to the PlayerMatch table.")
      return

   new_player_match = PlayerMatch(
      match_id=data.get('match_id'),
      steam_id=steam_id,
      hero_id=data.get('hero_id'),
      team=data.get('player_team'),
      kills=data.get('player_kills'),
      deaths=data.get('player_deaths'),
      assists=data.get('player_assists'),
      net_worth=data.get('net_worth'),
      denies=data.get('denies'),
      last_hits=data.get('last_hits'),
      is_complete=False 
   )

   session.add(new_player_match)

   logger.info(f"DB ADD---MatchID: {data.get('match_id')} & PlayerID: {steam_id} added to player_matches table.")
   return new_player_match

# Loop over list of stats - updating each one via update_player_record
def update_all_player_records(session, steam_id: int, player_match):
   # Create List to loop over
   stats = [
      ("kills", player_match.kills),
      ("deaths", player_match.deaths),
      ("assists", player_match.assists),
      ("net_worth", player_match.net_worth),
      ("denies", player_match.denies),
      ("last_hits", player_match.last_hits),
      ("kda", ((player_match.kills + player_match.assists) / player_match.deaths)),
   ]

   # Iterate over list to update/create record
   for stat_name, value in stats:
      update_player_record(session, steam_id, stat_name, value, player_match.hero_id)
   
   logger.info(f"DB ADD: Player {steam_id} records for match {player_match.match_id} parsed.")
   return

""" Assigns a new record for the player (Ex: 24 Kills) """
def update_player_record(session, steam_id: int, match_id: int, stat_name: str, value: int, hero_id: int = None):

   # Error Handling if there isnt a record
   if value is None:
      return

   # Query the record for user
   existing = session.query(PlayerRecord).filter_by(
      steam_id=steam_id,
      stat_name=stat_name
   ).first()

   # Check if parameter value is greater
   if existing:
      if value > existing.stat_value:
         # Update to new best match statistic
         existing.match_id = match_id
         existing.stat_value = value
         existing.hero_id = hero_id
         
   # First record for the stat
   else:
      new_record = PlayerRecord(
         steam_id=steam_id,
         stat_name=stat_name,
         stat_value=value,
         match_id=match_id,
         hero_id=hero_id
      )
      session.add(new_record)

""" Large Function: Handles all the match history processing, match, playermatch, playerrecords"""
""" Returns number of matches saved """
def save_matches_to_db(steam_id: int, deadlock_id: int, matches: list) -> int:
   matches_saved = 0 # Keeping track of match total

   # Opening new session to handle all the future DB commits with (One large commit)
   session = Session()

   try:
      for match in matches:
         # Create new match via DB
         # TODO later: Make it so if the match has already been added, end the entire function.
         #       New Matches are at the beginning of list.
         create_match(session, match)

         # Get data of single match via API
         match_data = get_match(match.get('match_id'))

         player_match = None

         # Check if match doesn't have salts
         if not match_data:
            # Save basic data
            player_match = create_player_match_without_salts(session, match, steam_id)
            matches_saved += 1
            continue

         match_id = match_data['match_info'].get('match_id')

         # Get the data for player from within players list of match_data
         for player in match_data['match_info'].get('players'):
            if player.get('account_id') == deadlock_id:
               # Add full match data
               player_match = create_player_match_with_salts(session, player, steam_id, match_id)
               matches_saved += 1
         
         logger.info(f"Parsed: MatchID: {match.get('match_id')} statistics added to player_matches & matches table. (Pre-Commit)")

         # Add Player Records from match
         update_all_player_records(session, steam_id, player_match)
            
         # Check if 

      session.commit()
      logger.info(f"COMMIT: Match History for {steam_id} parsed and committed to DB!")

      return matches_saved

   except Exception as e:
      session.rollback()
      print(f"Error saving matches for {steam_id}: {e}")
      return 0
   finally:
      session.close()

# Get all player record values
def get_player_records(steam_id: int) -> dict:
   session = Session()

   try:
      records = session.query(PlayerRecord)\
                       .options(joinedload(PlayerRecord.match))\
                       .filter_by(steam_id=steam_id)\
                       .all()

      result = {}

      for r in records:
         result[r.stat_name] = {
            "value": r.value,
            "hero_name": r.hero_name,
            "timestamp": r.match.timestamp if r.match else None,
            "match_id": r.match_id
         }
      
      return result
   finally:
      session.close()

# Get match data
def get_match(match_id):
   session = Session()

   match = session.query(Match).filter_by(match_id=match_id).first()

   session.close()

   if match:
      return match
   else:
      return None

# Get steam_id using discord_id
def get_steam_id_from_discord_id(discord_id: int) -> int:
   
   
   session = Session()

   player = session.query(Player).filter_by(discord_id=discord_id).first()

   session.close()

   if player:
      return player.steam_id
   else:
      return None
   
   
   
# Get deadlock-api id using steam_id
def get_deadlock_id_from_steam_id(steam_id: int) -> int:
   session = Session()
   
   player = session.query(Player).filter_by(steam_id=steam_id).first()

   session.close()

   if player:
      return player.deadlock_api_id
   else:
      return None

# Get Highest Kills match for user
def get_highest_kills_match(steam_id: int):
   session = Session()

   try:
      row = session.query(PlayerMatch)\
                      .filter_by(steam_id=steam_id)\
                      .order_by(desc(PlayerMatch.kills))\
                      .first()
      
      # Return data as dictionary
      data = {
         "match_id": row.match_id,
         "hero_id": row.hero_id,
         "kills": row.kills,
         "deaths": row.deaths,
         "assists": row.assists,
         "net_worth": row.net_worth,
         "team": row.team,
         "timestamp": row.matches.timestamp if row.matches else None,
         "duration_s": row.matches.duration_s if row.matches else None,
         "winning_team": row.matches.winning_team if row.matches else None
      }

      return data
   finally:
      session.close()

# TODO: Create a Function so that the row and related rows are returned as dictionary
