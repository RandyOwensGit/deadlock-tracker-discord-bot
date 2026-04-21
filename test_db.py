from database import Session, Player, Match, PlayerMatch, PlayerRecord, engine, Base
from datetime import datetime

Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)

session = Session()

# === Create test data ===
players = Player(
   steam_id=91668144, 
   discord_id=110900416346136576,
   deadlock_api_id=76561198051933872,
   display_name="TestRandy"
)
session.add(players)
session.commit()

matches = Match(
   match_id=123456789,
   timestamp=1776726909, 
   duration_s=2100, 
   mode=0, # use 0 for normal, 1 for brawl
   winning_team=0 # use 0 for loss, 1 for win
)
session.add(matches)
session.commit()

player_match = PlayerMatch(
   match_id=matches.match_id,
   steam_id=players.steam_id,
   hero_id=65,
   team=0, # use 0 for x, 1 for y
   result=0, # use 0 for loss, 1 for win
   kills=15,
   deaths=3,
   assists=8,
   net_worth=24500,
   denies=5,
   last_hits=150,
   lane=1, #use 0,1,2
   creep_kills=52,
   player_damage=74000,
   player_healing=16000,
   max_health=4800,
   shots_hit=3500,
   shots_missed=6000
)
session.add(player_match)

player_records = PlayerRecord(
   steam_id=players.steam_id,
   stat_name="Highest Kills",
   stat_value=31,
   match_id=matches.match_id,
   hero_id=player_match.hero_id
)
session.add(player_records)
session.commit()

print("-----Test data inserted successfully-------")

# === Read it back ===
print("\nPlayers:", [p.display_name for p in session.query(Player).all()])
print("Matches:", [m.match_id for m in session.query(Match).all()])
print("PlayerMatches:", session.query(PlayerMatch).count())
print("Records:", [(r.stat_name, r.value) for r in session.query(PlayerRecord).all()])

session.close()