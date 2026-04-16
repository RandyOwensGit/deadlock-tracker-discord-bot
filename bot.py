import discord
from discord.ext import commands
import json
import requests
import datetime
import logging
from dotenv import load_dotenv
import os

# ===================== Configuration =====================
# Move to .env file later
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
DEFAULT_STEAMID = os.getenv("DEFAULT_STEAMID")

# heroes.json path
HEROES_JSON_PATH = "heroes.json"

# API Settings
MATCH_HISTORY_URL = "https://api.deadlock-api.com/v1/players/{steam_id}/match-history"
MATCH_URL = "https://api.deadlock-api.com/v1/matches/{match_id}/metadata?is_custom=false"

# ===================== Logging Setup =====================
logging.basicConfig(
   level=logging.INFO,
   format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# ===================== Data Loading =====================
# Load heroes once when the bot starts (fast local lookup)
with open("heroes.json", "r", encoding="utf-8") as f:
   hero_data = json.load(f)

HERO_MAP = hero_data["hero_map"]

# ===================== Helper Functions =====================
# Convert seconds to HH:MM:SS format or MM:SS.
def format_match_time_duration(seconds: int) -> str:
   if seconds >= 3600:
      time = "01:"
   else:
      time = ""

      time += datetime.datetime.fromtimestamp(seconds).strftime('%M:%S')
      return time
   
# Fetch x last matches from Deadlock API
def get_last_matches(steam_id: str, limit: int) -> list:
   url = MATCH_HISTORY_URL.format(steam_id = steam_id)
   try:
      response = requests.get(url, timeout=10)
      response.raise_for_status()
      all_matches = response.json()
      return all_matches[:limit]
   except requests.RequestException as e:
      logger.error(f"API request failed for {steam_id}: {e}")
      return []
   
# Fetch match data
def get_match(match_id: int) -> list:
   url = MATCH_URL.format(match_id = match_id)
   try:
      response = requests.get(url, timeout=10)
      response.raise_for_status()
      return response.json()
   except requests.RequestException as e:
      logger.error(f"API request failed for {match_id}: {e}")
      return []
   
# Formatted Match Line
def format_match_line(match: dict) -> str:
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
   match_players = match_info.get('players')

   friends_in_match = []

   for player in match_players:
      player = get_friend_name_by_game_id(player['account_id'])

      if player == 'None':
         continue
      else:
         friends_in_match.append(player)

   return f"{hero_name:<12} | {result:<4} | {kda:<8} | {souls_formatted:<7}souls | {duration} | {friends_in_match}"

# Get Friend by steamid64
def get_friend_name_by_game_id(id: int) -> str:
   # Randy
   if id == 91668144:
      return 'Randy'

   # Clayton
   elif id == 415616741:
      return 'Clayton'

   # Hunty Primary Account
   elif id == 158510109:
      return 'Hunty Main'
   
   # Hunty Second Account
   elif id == 1245647193:
      return 'Hunty Second'
   
   # Hunty Third Account
   elif id == 81913945:
      return 'Hunty Third'

   # Engin
   elif id == 365467670:
      return 'Engin'

   # Blake
   elif id == 125258721:
      return 'Blake'

   # Burak
   elif id == 319942495:
      return 'Burak'   
   
   # Sean
   elif id == 31321321:
      return 'Sean'
   
   return 'None'

# ===================== BOT SETUP =====================
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="/", intents=intents)

@bot.event
async def on_ready():
   logger.info(f"Bot is online as {bot.user} (ID: {bot.user.id})")
   print(f"🚀 Bot is ready!")

# Show x amount of previous matches for steam_id64
@bot.command(name="lastmatches", aliases=["matches", "lm"])
async def last_matches(ctx, steam_id: str, amt_of_matches: int):

   ## Error Handling for Steam ID
   if steam_id is None:
      steam_id = DEFAULT_STEAMID
      title = f"SteamID is invalid (use SteamID64 for now)"
      await ctx.send(f"**{title}**")
      return
   else:
      title = f"Last {amt_of_matches} matches for SteamID {steam_id}"

   matches = get_last_matches(steam_id, amt_of_matches)
   if not matches:
      await ctx.send("No matches were found or error getting data.")
      return
   
   # Build matches message
   lines = [format_match_line(match) for match in matches]
   response_text = "\n".join(lines)

   # Creating Embed
   embed = discord.Embed(
      title=title,
      description=f"```{response_text}```",
      color=discord.Color.blue(),
      timestamp=datetime.datetime.now(datetime.UTC)
   )
   
   await ctx.send(embed=embed)

# Testing command for parsing a match

# ====================== RUN THE BOT ======================
if __name__ == "__main__":
   bot.run(BOT_TOKEN)