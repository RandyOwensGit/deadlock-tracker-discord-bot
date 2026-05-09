import asyncio
from discord.ext import tasks

from database import Player, Session

# Automated processing for user matches

class AutoTrackerCog(commands.Cog):
   def __init__(self, bot):
      self.bot = bot
      self.auto_check.start()

   def cog_unload(self):
      self.auto_check.cancel()

   @tasks.loop(minutes=15)
   async def auto_check(self):
      await self.bot.wait_until_ready()

      await self.check_for_new_matches()

   async def check_for_new_matches(self):
      session = Session()

      try:
         players = session.query(Player).all()

         for player in players:
            await self.process_player_new_matches(player)
      
      finally:
         session.close()

async def tasks(bot):
   await bot.add_cog(TasksCog(bot))
