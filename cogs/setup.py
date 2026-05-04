
import asyncio
from concurrent.futures import ThreadPoolExecutor
import datetime
import discord
import bot
from bot import logger
from discord.ext import commands
from utils.api import get_all_matches, get_last_matches, get_match
from utils.db import create_player, get_deadlock_id_from_steam_id, get_highest_kills_match, get_player_lifetime_stats, get_player_records, get_steam_id_from_discord_id, save_matches_to_db
from utils.helpers import format_match_line
from utils.heroes import HERO_MAP
from datetime import datetime

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
         await ctx.send(f"Error adding {ctx.author.name}.")
         return
      
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
         return
      
      await ctx.send("Adding matches...")

      def blocking_task():
         # Get match history as a list
         matchList = get_all_matches(steam_id)

         # Pass match history list to db function to handle
         amt_of_matches_saved = save_matches_to_db(steam_id, deadlock_id, matchList)

         return amt_of_matches_saved
      try:
         matches_saved = await asyncio.get_event_loop().run_in_executor(executor, blocking_task)
         await ctx.send(f"...Finished adding matches for {ctx.author.name}")

         if matches_saved == 0:
            await ctx.send(f"{ctx.author.name} has no new matches to be added. Play more Deadlock!")
         else:
            await ctx.send(f"{matches_saved} matches populated into the DB for SteamID: {steam_id}\n")
      except Exception as e:
         await ctx.send(f"Error parsing matches for user {ctx.author.name}::: {e}")

# Test command to display all player records
   @commands.command(name="records")
   async def player_records(self, ctx):
      steam_id = get_steam_id_from_discord_id(ctx.author.id)

      records = get_player_records(steam_id)

      if not records:
         await ctx.send(f"No records found for {ctx.author.name}")
         return

      embed = discord.Embed(
         title=f"{ctx.author.name}'s Records",
         color=discord.Color.gold()
      )

      for stat_name, data in records.items():
         value = data["stat_value"]
         hero = HERO_MAP.get(str(data.get('hero_id')))
         date = datetime.fromtimestamp(data["timestamp"]).strftime("%Y-%m-%d")

         embed.add_field(
            name=stat_name.replace("_", " ").title(),
            value=f"*{value:,}* on {hero}\n{date}",
            inline=True
         )

      await ctx.send(embed=embed)

# Command to see player Career
   @commands.command(name="career")
   async def profile(self, ctx):
      steam_id = get_steam_id_from_discord_id(ctx.author.id)

      stats = get_player_lifetime_stats(steam_id)

      total_shots = stats["total_shots_hit"] + stats["total_shots_missed"]
      accuracy = (stats["total_shots_hit"] / total_shots * 100)

      embed = discord.Embed(title=f"{ctx.author.name}'s Career", color=discord.Color.gold())
      embed.add_field(name="Games Played", value=stats["total_matches"], inline=True)
      embed.add_field(name="Kills", value=f"{stats["total_kills"]:,}", inline=True)
      embed.add_field(name="Deaths", value=f"{stats["total_deaths"]:,}", inline=True)
      embed.add_field(name="Assists", value=f"{stats["total_assists"]:,}", inline=True)
      embed.add_field(name="Souls", value=f"{stats["total_souls"]:,}", inline=True)
      embed.add_field(name="Player Damage", value=f"{stats["total_damage"]:,}", inline=True)
      embed.add_field(name="Player Healing", value=f"{stats["total_healing"]:,}", inline=True)
      embed.add_field(name="Accuracy", value=round(float(accuracy), 2), inline=True)
      embed.add_field(name="Win Rate", value=stats["winrate"], inline=True)
      embed.add_field(name="Average (K/D/A)", value=f"{stats["avg_kills"]}/{stats["avg_deaths"]}/{stats["avg_assists"]}", inline=True)

      await ctx.send(embed=embed)


async def setup(bot):
   await bot.add_cog(SetupCog(bot))