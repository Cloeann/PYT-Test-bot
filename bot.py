import os
import discord

from discord.ext import commands

from emoji_game import setup_emoji_game


# ========================================
# CONFIGURATION
# ========================================

TOKEN = os.getenv(
    "BOT_TOKEN"
)

GUILD_ID = 1543689046625230880


# ========================================
# INTENTS
# ========================================

intents = discord.Intents.default()

intents.message_content = True

intents.members = True


# ========================================
# BOT
# ========================================

bot = commands.Bot(

    command_prefix="!",

    intents=intents
)


# ========================================
# LOAD EMOJI GAME
# ========================================

setup_emoji_game(
    bot
)


# ========================================
# READY
# ========================================

@bot.event
async def on_ready():

    try:

        guild = discord.Object(
            id=GUILD_ID
        )


        bot.tree.copy_global_to(
            guild=guild
        )


        synced = await bot.tree.sync(
            guild=guild
        )


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
