import os
import discord

from discord.ext import commands


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


# ========================================
# BOT
# ========================================

bot = commands.Bot(

    command_prefix="!",

    intents=intents
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
# EMOJI TEST COMMAND
# ========================================

@bot.tree.command(
    name="emoji",
    description="Start an emoji guessing game!"
)
async def emoji(

    interaction: discord.Interaction

):

    await interaction.response.send_message(

        "🎮 Emoji game test! It works! 🎉"

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
# RUN
# ========================================

bot.run(
    TOKEN
)
