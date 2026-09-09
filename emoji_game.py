import discord
import json
import random
import asyncio
import re
import os

from discord.ext import commands
from discord import app_commands


# ========================================
# FILE PATHS
# ========================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)


PUZZLES_PATH = os.path.join(
    BASE_DIR,
    "puzzles.json"
)


SCORES_PATH = os.path.join(
    BASE_DIR,
    "scores.json"
)


# ========================================
# LOAD PUZZLES
# ========================================

def load_puzzles():

    try:

        with open(
            PUZZLES_PATH,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)

    except Exception as error:

        print(
            f"❌ Could not load puzzles: {error}"
        )

        return {}


# ========================================
# LOAD SCORES
# ========================================

def load_scores():

    try:

        if not os.path.exists(
            SCORES_PATH
        ):

            return {}


        with open(
            SCORES_PATH,
            "r",
            encoding="utf-8"
        ) as file:

            content = file.read()


            if not content.strip():

                return {}


            return json.loads(
                content
            )


    except Exception as error:

        print(
            f"❌ Could not load scores: {error}"
        )

        return {}


# ========================================
# SAVE SCORES
# ========================================

def save_scores(scores):

    try:

        with open(
            SCORES_PATH,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                scores,
                file,
                indent=4
            )


    except Exception as error:

        print(
            f"❌ Could not save scores: {error}"
        )


# ========================================
# NORMALIZE ANSWERS
# ========================================

def normalize(text):

    text = text.lower()

    text = re.sub(
        r"[^a-z0-9\s]",
        "",
        text
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


# ========================================
# CHECK ANSWER
# ========================================

def check_answer(
    guess,
    puzzle
):

    guess = normalize(
        guess
    )


    answers = [

        puzzle.get(
            "answer",
            ""
        )

    ]


    answers.extend(

        puzzle.get(
            "aliases",
            []
        )

    )


    for answer in answers:

        if (

            guess == normalize(answer)

        ):

            return True


    return False


# ========================================
# ACTIVE GAMES
# ========================================

active_games = {}


# ========================================
# CATEGORY DATA
# ========================================

CATEGORIES = {

    "movies": {

        "label": "🎬 Movies",

        "emoji": "🎬"

    },

    "anime": {

        "label": "🍥 Anime",

        "emoji": "🍥"

    },

    "countries": {

        "label": "🌍 Countries",

        "emoji": "🌍"

    },

    "words": {

        "label": "💬 Words",

        "emoji": "💬"

    }

}


# ========================================
# CATEGORY VIEW
# ========================================

class CategoryView(
    discord.ui.View
):


    def __init__(
        self,
        cog,
        channel_id
    ):

        super().__init__(
            timeout=60
        )


        self.cog = cog

        self.channel_id = channel_id


    async def interaction_check(
        self,
        interaction
    ):

        if (

            interaction.channel_id
            !=
            self.channel_id

        ):

            return False


        return True


    # ====================================
    # MOVIES
    # ====================================

    @discord.ui.button(

        label="Movies",

        emoji="🎬",

        style=discord.ButtonStyle.primary

    )
    async def movies(

        self,

        interaction,

        button

    ):

        await self.start_game(

            interaction,

            "movies"

        )


    # ====================================
    # ANIME
    # ====================================

    @discord.ui.button(

        label="Anime",

        emoji="🍥",

        style=discord.ButtonStyle.primary

    )
    async def anime(

        self,

        interaction,

        button

    ):

        await self.start_game(

            interaction,

            "anime"

        )


    # ====================================
    # COUNTRIES
    # ====================================

    @discord.ui.button(

        label="Countries",

        emoji="🌍",

        style=discord.ButtonStyle.primary

    )
    async def countries(

        self,

        interaction,

        button

    ):

        await self.start_game(

            interaction,

            "countries"

        )


    # ====================================
    # WORDS
    # ====================================

    @discord.ui.button(

        label="Words",

        emoji="💬",

        style=discord.ButtonStyle.primary

    )
    async def words(

        self,

        interaction,

        button

    ):

        await self.start_game(

            interaction,

            "words"

        )


    # ====================================
    # START GAME
    # ====================================

    async def start_game(

        self,

        interaction,

        category

    ):

        if (

            self.channel_id
            in
            active_games

        ):

            await interaction.response.send_message(

                "⚠️ There is already an active game in this channel!",

                ephemeral=True

            )

            return


        puzzles = self.cog.puzzles.get(

            category,

            []

        )


        if not puzzles:

            await interaction.response.send_message(

                "❌ No puzzles found for this category.",

                ephemeral=True

            )

            return


        puzzle = random.choice(
            puzzles
        )


        active_games[
            self.channel_id
        ] = {

            "puzzle": puzzle,

            "category": category,

            "message": None,

            "finished": False

        }


        category_data = CATEGORIES[
            category
        ]


        embed = discord.Embed(

            title="🎮 Emoji Guessing Game",

            description=

                f"## {puzzle['emoji']}\n\n"

                f"**Category:** "
                f"{category_data['label']}\n\n"

                "⏱️ You have **60 seconds** to guess!\n"

                "💬 Everyone can type their guesses in chat!"

        )


        await interaction.response.edit_message(

            content=None,

            embed=embed,

            view=None

        )


        message = await interaction.original_response()


        active_games[
            self.channel_id
        ][
            "message"
        ] = message


        asyncio.create_task(

            self.cog.game_timer(
                self.channel_id
            )

        )


# ========================================
# EMOJI GAME COG
# ========================================

class EmojiGame(
    commands.Cog
):


    def __init__(
        self,
        bot
    ):

        self.bot = bot

        self.puzzles = load_puzzles()

        self.scores = load_scores()


    # ====================================
    # /EMOJI
    # ====================================

    @app_commands.command(

        name="emoji",

        description=
        "Start an emoji guessing game!"

    )
    async def emoji(

        self,

        interaction:
        discord.Interaction

    ):

        channel_id = interaction.channel_id


        if (

            channel_id
            in
            active_games

        ):

            await interaction.response.send_message(

                "⚠️ There is already an active game in this channel!",

                ephemeral=True

            )

            return


        embed = discord.Embed(

            title="🎮 Emoji Guessing Game",

            description=

                "Choose a category to begin!\n\n"

                "🎬 **Movies**\n"

                "🍥 **Anime**\n"

                "🌍 **Countries**\n"

                "💬 **Words**"

        )


        view = CategoryView(

            self,

            channel_id

        )


        await interaction.response.send_message(

            embed=embed,

            view=view

        )


    # ====================================
    # MESSAGE LISTENER
    # ====================================

    @commands.Cog.listener()
    async def on_message(

        self,

        message

    ):

        if message.author.bot:

            return


        channel_id = message.channel.id


        if (

            channel_id
            not in
            active_games

        ):

            return


        game = active_games[
            channel_id
        ]


        if game[
            "finished"
        ]:

            return


        puzzle = game[
            "puzzle"
        ]


        if not check_answer(

            message.content,

            puzzle

        ):

            return


        # ================================
        # CORRECT ANSWER
        # ================================

        game[
            "finished"
        ] = True


        user_id = str(
            message.author.id
        )


        if (

            user_id
            not in
            self.scores

        ):

            self.scores[
                user_id
            ] = {

                "score": 0,

                "name":
                message.author.display_name

            }


        self.scores[
            user_id
        ][
            "score"
        ] += 1


        self.scores[
            user_id
        ][
            "name"
        ] = message.author.display_name


        save_scores(
            self.scores
        )


        embed = discord.Embed(

            title="🎉 Correct!",

            description=

                f"🏆 **{message.author.display_name}** "
                f"guessed correctly!\n\n"

                f"🧩 {puzzle['emoji']}\n\n"

                f"✅ **Answer:** "
                f"{puzzle['answer']}\n\n"

                "➕ **1 point!**"

        )


        await message.channel.send(

            embed=embed

        )


        active_games.pop(

            channel_id,

            None

        )


    # ====================================
    # GAME TIMER
    # ====================================

    async def game_timer(

        self,

        channel_id

    ):

        await asyncio.sleep(
            60
        )


        if (

            channel_id
            not in
            active_games

        ):

            return


        game = active_games[
            channel_id
        ]


        if game[
            "finished"
        ]:

            return


        game[
            "finished"
        ] = True


        puzzle = game[
            "puzzle"
        ]


        message = game.get(
            "message"
        )


        embed = discord.Embed(

            title="⏰ Time's Up!",

            description=

                "Nobody guessed it in time! 😭\n\n"

                f"🧩 {puzzle['emoji']}\n\n"

                f"✅ **The answer was:** "
                f"{puzzle['answer']}"

        )


        if message:

            await message.channel.send(

                embed=embed

            )


        active_games.pop(

            channel_id,

            None

        )


    # ====================================
    # /EMOJI_HIGHSCORE
    # ====================================

    @app_commands.command(

        name="emoji_highscore",

        description=
        "View the emoji game highscores!"

    )
    async def emoji_highscore(

        self,

        interaction:
        discord.Interaction

    ):

        if not self.scores:

            await interaction.response.send_message(

                "📊 No scores yet! Play `/emoji` to get started!"

            )

            return


        sorted_scores = sorted(

            self.scores.items(),

            key=lambda item:
            item[1].get(
                "score",
                0
            ),

            reverse=True

        )


        lines = []


        medals = [

            "🥇",

            "🥈",

            "🥉"

        ]


        for index, (

            user_id,

            data

        ) in enumerate(

            sorted_scores[:10]

        ):


            if index < 3:

                position = medals[
                    index
                ]

            else:

                position = (
                    f"**{index + 1}.**"
                )


            name = data.get(

                "name",

                "Unknown User"

            )


            score = data.get(

                "score",

                0

            )


            lines.append(

                f"{position} "
                f"**{name}** "
                f"— {score} point"
                f"{'s' if score != 1 else ''}"

            )


        embed = discord.Embed(

            title="🏆 Emoji Game Highscores",

            description="\n".join(
                lines
            )

        )


        await interaction.response.send_message(

            embed=embed

        )


# ========================================
# SETUP
# ========================================

async def setup(
    bot
):

    await bot.add_cog(

        EmojiGame(bot)

    )
