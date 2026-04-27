import discord
from discord.ext import commands
import datetime
import logging
from config import BOT_TOKEN, COMMAND_PREFIX
from database import Session, Player

# ===================== Logging Setup =====================
logging.basicConfig(
   level=logging.INFO,
   format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# ===================== BOT SETUP =====================
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix=COMMAND_PREFIX, intents=intents)

# Bot start event
@bot.event
async def on_ready():
   logger.info(f"Bot is online as {bot.user} (ID: {bot.user.id})")
   print(f"🚀 Bot is ready!")

# Loading bot cogs ( commands )
async def load_cogs():
   for filename in ["setup"]:
      try:
         await bot.load_extension(f"cogs.{filename}")
         logger.info(f"Loaded cog: cogs.{filename}")
      except Exception as e:
         logger.error(f"Failed to load cog: {filename}: {e}")

# Error with commands
async def on_command_error(ctx, error):
   if isinstance(error, commands.CommandNotFound):
      return
   logger.error(f"Command error: {error}")
   await ctx.send(f"Erorr: {error}")

# ====================== RUN THE BOT ======================
async def main():
   await load_cogs()
   await bot.start(BOT_TOKEN)

if __name__ == "__main__":
   import asyncio
   asyncio.run(main())