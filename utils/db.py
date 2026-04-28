from sqlalchemy import desc

from database import Match, Player, PlayerMatch, Session
from bot import logger

# functions related to accessing the Database

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
def create_match(data) -> int:
   session = Session()

   try:
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
      session.commit()

      logger.info(f"DB CREATE---MatchID: {data.get('match_id')} added to matches table.")
      return 0

   except Exception as e:
      session.rollback()
      logger.error(f"DB - Error adding match to matches table: {e}")
      return 2
   finally:
      session.close()

# creating new record for player_matches table JSON
# When match has salts data
# Return 0 for success, 1 for already exists, 2 for error adding to DB
def create_player_match_with_salts(data, steam_id, match_id) -> int:
   session = Session()

   try:
      # Check if player has already had their match statistics added for this match
      existing = session.query(PlayerMatch).filter_by(
         match_id=match_id,
         steam_id=steam_id
      ).first()

      if existing:
         logger.info(f"MatchID: {data.get('match_id')} & PlayerID: {id} data have already been added to the PlayerMatch table.")
         return 1
      
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
      session.commit()

      logger.info(f"DB CREATE---MatchID: {match_id} & PlayerID: {steam_id} added to player_matches table.")
      return 0

   except Exception as e:
      session.rollback()
      logger.error(f"DB - Error adding PlayerMatch to player_matches: {e}")
      return 2
   finally:
      session.close()


# creating new record for player_matches table JSON
# when match has NO SALTS
# Return 0 for success, 1 for already exists, 2 for error adding to DB
def create_player_match_without_salts(data, steam_id) -> int:
   session = Session()

   try:
      # Check if player has already had their match statistics added for this match
      existing = session.query(PlayerMatch).filter_by(
         match_id=data.get('match_id'),
         steam_id=steam_id
      ).first()

      if existing:
         logger.info(f"MatchID: {data.get('match_id')} & PlayerID: {id} data have already been added to the PlayerMatch table.")
         return 1

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
      session.commit()

      logger.info(f"DB Create---MatchID: {data.get('match_id')} & PlayerID: {steam_id} added to player_matches table.")
      return 0

   except Exception as e:
      session.rollback()
      logger.error(f"DB - Error adding PlayerMatch to player_matches: {e}")
      return 2
   finally:
      session.close()

# Get match data
def get_match(match_id):
   session = Session()

   match = session.query(Match).filter_by(match_id=match_id).first()

   if match:
      return match
   else:
      return None

# Get steam_id using discord_id
def get_steam_id_from_discord_id(discord_id: int) -> int:
   session = Session()

   player = session.query(Player).filter_by(discord_id=discord_id).first()

   if player:
      return player.steam_id
   else:
      return None
   
# Get deadlock-api id using steam_id
def get_deadlock_id_from_steam_id(steam_id: int) -> int:
   session = Session()
   
   player = session.query(Player).filter_by(steam_id=steam_id).first()

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
