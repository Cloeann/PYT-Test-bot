import os
import discord

from discord.ext import commands


# ========================================
# CONFIGURATION
# ========================================

TOKEN = os.getenv(
    "BOT_TOKEN"
)


# ========================================
# INTENTS
# ========================================

intents = discord.Intents.default()

intents.message_content = True


# ========================================
# BOT
# ========================================

bot = commands.Bot(

    command_prefix="!",

    intents=intents
)


# ========================================
# READY
# ========================================

@bot.event
async def on_ready():

    print(
        f"🤖 Logged in as {bot.user}"
    )


# ========================================
# RUN
# ========================================

bot.run(
    TOKEN
)
