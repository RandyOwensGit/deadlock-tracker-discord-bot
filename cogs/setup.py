
import asyncio
from concurrent.futures import ThreadPoolExecutor
import datetime
import discord
import bot
from bot import logger
from discord.ext import commands
from database import Player, Session
from utils.api import get_all_matches, get_last_matches, get_match
from utils.db import create_match, create_player, create_player_match_with_salts, create_player_match_without_salts, get_deadlock_id_from_steam_id, get_steam_id_from_discord_id
from utils.helpers import format_match_line, save_matches_to_db

executor = ThreadPoolExecutor(max_workers=3)

class SetupCog(commands.Cog):
   def __init__(self, bot):
      self.bot = bot

   @commands.command(name="matches")
   async def last_matches(self, ctx, steam_id: str, amt_of_matches: int):
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
      lines = [format_match_line(match, int(steam_id)) for match in matches]
      response_text = "\n".join(lines)

      # Creating Embed
      embed = discord.Embed(
         title=title,
         description=f"```{response_text}```",
         color=discord.Color.blue(),
         timestamp=datetime.datetime.now(datetime.UTC)
      )
      
      await ctx.send(embed=embed)

# Command for setting up 'Profile'
# Requires steamid64
   @commands.command(name="setup")
   async def setup(self, ctx, steam_id: str):
      print("Running setup command...")
      print(f"Entered ID: {steam_id}")

   # Check for SteamID64
      if not steam_id.isdigit() or len(steam_id) != 17:
         await ctx.send("Invalid steamID64. 17 Digit number")
         return
      
      steam_id_int = int(steam_id)

      # Get deadlock_api_id
      data = get_last_matches(steam_id, 1)
      account_id = data[0]['account_id']

      add_player = create_player(
         steam_id_int, ctx.author.id, account_id, ctx.author.display_name
      )

      if add_player == 1:
         await ctx.send(f"{ctx.author.name} already setup with SteamID64: {steam_id}")
         return
      
      if add_player == 2:
         await ctx.send(f"{ctx.author.name} error adding player to players table.")
      
      await ctx.send(
         f"{ctx.author.name} added to the Deadlock Tracker.\n"
         f"SteamID: {steam_id}\n"
         f"DiscordID: {ctx.author.id}\n"
         f"DeadlockID: {account_id}\n"
         f"Now run !update_matches if you have any deadlock games played!"
      )

# Command for setting up Match History
# Requires user to have ran the setup command
   @commands.command(name="update_matches")
   async def update_matches(self, ctx):
      # Get steamid64
      steam_id = get_steam_id_from_discord_id(ctx.author.id)

      # Get deadlock-api id
      deadlock_id = get_deadlock_id_from_steam_id(steam_id)

      if steam_id == None:
         await ctx.send(f"You are not setup with this bot yet. Enter !setup <steamid64>")
      
      await ctx.send("Populating the database... Could take a bit.")

      def blocking_task():
         amtOfMatchesSaved = save_matches_to_db(steam_id, deadlock_id, get_all_matches(steam_id))

         return amtOfMatchesSaved
      try:
         matchesSaved = await asyncio.get_event_loop().run_in_executor(executor, blocking_task)
         await ctx.send(f"Finished parsing matches into database for user {ctx.author.name}")
         await ctx.send(f"{matchesSaved} matches populated into the DB for SteamID: {steam_id}\n")
      except Exception as e:
         await ctx.send(f"Error parsing matches for user {ctx.author.name}::: {e}")


async def setup(bot):
   await bot.add_cog(SetupCog(bot))