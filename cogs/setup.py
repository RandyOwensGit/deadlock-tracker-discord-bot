# Other commands for now:
# Show x amount of previous matches for steam_id64
import datetime

import discord

import bot
from database import Player, Session
from utils.api import get_last_matches
from utils.helpers import format_match_line

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



# All about the large setup command
# Get user + deadlock "account"
# Setup "profile" via DB
# Add all match history to DB
# Get stat records


# Command for setting up 'Profile'
# Requires steamid64
@bot.command(name="setup")
async def setup(ctx, steam_id: str):
   # Validation
   if not steam_id.isdigit() or len(steam_id) != 17:
      await ctx.send("Invalid steamID64. 17 Digit number")
      return
   
   steam_id_int = int(steam_id)

   session = Session()
   try:
      # Check if player already exists in players table
      existing = session.query(Player).filter_by(steam_id=steam_id_int).first()

      if existing:
         await ctx.send(f"{ctx.author.name} already setup with SteamID64: {steam_id}")
         return

      # Get Deadlock_api_id
      data = get_last_matches(steam_id, 1)
      account_id = data[0]['account_id']

   
      # Create new player
      new_player = Player(
         steam_id=steam_id_int,
         discord_id=ctx.author.id,
         deadlock_api_id=account_id,
         display_name=ctx.author.display_name
      )

      session.add(new_player)
      session.commit()

      await ctx.send(
         f"{ctx.author.display_name} added to the Deadlock Tracker.\n"
         f"SteamID: {steam_id}\n"
         f"DiscordID: {ctx.author.id}\n"
         f"DeadlockID: {account_id}"
      )
   
   except Exception as e:
      session.rollback()
      await ctx.send(f"Error saving to database: {e}")
   finally:
      session.close()