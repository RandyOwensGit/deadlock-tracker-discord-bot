import sqlalchemy as sa
from sqlalchemy.orm import DeclarativeBase, relationship, sessionmaker
from datetime import datetime
import json

# Sets up DB

# ================ BASE ================
class Base(DeclarativeBase):
   pass

# ================ TABLES ================

# Player Table
class Player(Base):
   __tablename__ = "players"

   id = sa.Column(sa.Integer, primary_key=True)
   steam_id = sa.Column(sa.BigInteger, unique=True, nullable=False, index=True)
   discord_id = sa.Column(sa.BigInteger, unique=True, index=True, nullable=True)
   deadlock_api_id = sa.Column(sa.BigInteger, index=True, nullable=True)
   display_name = sa.Column(sa.String(100), nullable=True)
   xp = sa.Column(sa.BigInteger, default=0)

   player_matches = relationship("PlayerMatch", back_populates="players")

# Player Records Table
class PlayerRecord(Base):
   __tablename__ = "player_records"

   id = sa.Column(sa.Integer, primary_key=True)
   steam_id = sa.Column(sa.BigInteger, nullable=False, index=True)

   stat_name = sa.Column(sa.String(30), nullable=False, index=True) # record name
   stat_value = sa.Column(sa.Integer, nullable=False)

   match_id = sa.Column(sa.BigInteger, nullable=False)
   hero_id = sa.Column(sa.Integer, nullable=True) # Not required for all records

   # composite unique constraint on steam_id and stat_name
   __table_args__ = (
      sa.UniqueConstraint("steam_id", "stat_name", name="uix_player_stat"),
   )

# Matches Table
class Match(Base):
   __tablename__ = "matches"

   match_id = sa.Column(sa.BigInteger, primary_key=True, autoincrement=False)
   timestamp = sa.Column(sa.BigInteger, default=0, index=True)
   duration_s = sa.Column(sa.Integer, nullable=True)
   mode = sa.Column(sa.Integer, nullable=True)
   winning_team = sa.Column(sa.Integer, nullable=True) 
   # Could store full API response

   player_matches = relationship("PlayerMatch", back_populates="matches")

#  Player Matches Table
class PlayerMatch(Base):
   __tablename__ = "player_matches"

   id = sa.Column(sa.Integer, primary_key=True)
   match_id = sa.Column(sa.BigInteger, sa.ForeignKey("matches.match_id"), nullable=False)
   steam_id = sa.Column(sa.BigInteger, sa.ForeignKey("players.steam_id"), nullable=False)

   hero_id = sa.Column(sa.Integer)
   team = sa.Column(sa.Integer)
   kills = sa.Column(sa.Integer, default=0)
   deaths = sa.Column(sa.Integer, default=0)
   assists = sa.Column(sa.Integer, default=0)
   net_worth = sa.Column(sa.Integer, default=0)
   denies = sa.Column(sa.Integer, default=0)
   last_hits = sa.Column(sa.Integer, default=0)
   lane = sa.Column(sa.Integer, default=0)
   creep_kills = sa.Column(sa.Integer, default=0)
   player_damage = sa.Column(sa.Integer, default=0)
   player_healing = sa.Column(sa.Integer, default=0)
   max_health = sa.Column(sa.Integer, default=0)
   shots_hit = sa.Column(sa.Integer, default=0)
   shots_missed = sa.Column(sa.Integer, default=0)

   is_complete = sa.Column(sa.Boolean, default=False)

   # Prevent duplicate player match statistics
   __table_args__ = (
      sa.UniqueConstraint("match_id", "steam_id", name="uix_match_player"),
   )

   # Relationships
   matches = relationship("Match", back_populates="player_matches")
   players = relationship("Player", back_populates="player_matches")

# Eventual table for items at end of game

# ================ ENGINE (SQLite) ================
engine = sa.create_engine(
   "sqlite:///deadlock.db",
   echo=False,
   connect_args={"check_same_thread": False} # Threaded access
)

# Create tables if not exist
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)

print("Database setup complete.")
print("  Database filed: deadlock.db")
print("  Tables: players, matches, player_records, player_matches")