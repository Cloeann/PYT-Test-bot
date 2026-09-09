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

    try:

        synced = await bot.tree.sync()

        print(
            f"🔄 Synced {len(synced)} slash command(s)"
        )

    except Exception as error:

        print(
            f"❌ Could not sync commands: {error}"
        )


    print(
        f"🤖 Logged in as {bot.user}"
    )


# ========================================
# PING COMMAND
# ========================================

@bot.tree.command(
    name="ping",
    description="Check if the bot is alive!"
)
async def ping(

    interaction: discord.Interaction

):

    await interaction.response.send_message(

        "🏓 Pong! The bot is alive!"

    )


# ========================================
# RUN
# ========================================

bot.run(
    TOKEN
)
