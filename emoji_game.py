import discord
import json
import os
import asyncio
import random
import re

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
    "emoji_scores.json"
)


# ========================================
# GAME SETTINGS
# ========================================

GAME_TIME = 60


# ========================================
# ACTIVE GAMES
# ========================================

active_games = {}


# ========================================
# LOAD JSON
# ========================================

def load_json(path, default):

    try:

        if not os.path.exists(path):

            return default


        with open(
            path,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)


    except Exception as error:

        print(
            f"❌ Could not load {path}: {error}"
        )

        return default


# ========================================
# SAVE JSON
# ========================================

def save_json(path, data):

    try:

        with open(
            path,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                data,
                file,
                indent=4,
                ensure_ascii=False
            )


    except Exception as error:

        print(
            f"❌ Could not save {path}: {error}"
        )


# ========================================
# NORMALIZE ANSWERS
# ========================================

def normalize_answer(text):

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

    message,
    answers

):

    guess = normalize_answer(
        message
    )


    for answer in answers:

        normalized = normalize_answer(
            answer
        )


        if guess == normalized:

            return True


    return False


# ========================================
# LOAD SCORES
# ========================================

def load_scores():

    return load_json(

        SCORES_PATH,

        {}
    )


# ========================================
# SAVE SCORES
# ========================================

def save_scores(scores):

    save_json(

        SCORES_PATH,

        scores

    )


# ========================================
# ADD SCORE
# ========================================

def add_score(

    user

):

    scores = load_scores()

    user_id = str(
        user.id
    )


    if user_id not in scores:

        scores[user_id] = {

            "name":
                user.display_name,

            "score":
                0

        }


    scores[user_id][
        "name"
    ] = user.display_name


    scores[user_id][
        "score"
    ] += 1


    save_scores(
        scores
    )


    return scores[user_id][
        "score"
    ]


# ========================================
# CATEGORY BUTTONS
# ========================================

class CategoryView(
    discord.ui.View
):


    def __init__(

        self,
        author

    ):

        super().__init__(

            timeout=30

        )


        self.author = author


    async def interaction_check(

        self,
        interaction

    ):


        if (

            interaction.user.id !=
            self.author.id

        ):

            await interaction.response.send_message(

                "❌ Only the person who started the game can choose a category!",

                ephemeral=True

            )

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

        await start_game(

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

        await start_game(

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

        await start_game(

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

        await start_game(

            interaction,

            "words"

        )

# ========================================
# GENERATE HINT
# ========================================

def generate_hint(answer):

    hint = ""


    for character in answer:


        # Keep spaces

        if character == " ":

            hint += " "


        # Keep hyphens

        elif character == "-":

            hint += "-"


        else:

            hint += "_"


    # Reveal first letter of every word

    words = hint.split(" ")

    answer_words = answer.split(" ")


    new_words = []


    for index, word in enumerate(words):


        answer_word = answer_words[index]


        if answer_word:


            new_word = (

                answer_word[0]

                +

                word[1:]

            )


            new_words.append(

                new_word

            )


        else:

            new_words.append(

                word

            )


    return " ".join(

        new_words

    )

# ========================================
# START GAME
# ========================================

async def start_game(

    interaction,
    category

):


    channel_id = interaction.channel.id


    # Check active game

    if channel_id in active_games:

        await interaction.response.send_message(

            "❌ There is already an active emoji game in this channel!",

            ephemeral=True

        )

        return


    # Load puzzles

    puzzles = load_json(

        PUZZLES_PATH,

        {}
    )


    # Check category

    if category not in puzzles:

        await interaction.response.send_message(

            "❌ This category has no puzzles!",

            ephemeral=True

        )

        return


    if not puzzles[category]:

        await interaction.response.send_message(

            "❌ This category has no puzzles!",

            ephemeral=True

        )

        return


    # Pick puzzle

    puzzle = random.choice(

        puzzles[category]

    )


    emojis = puzzle[
        "emojis"
    ]


    answers = puzzle[
        "answers"
    ]


    # Register game

    active_games[channel_id] = {

        "answers":
            answers,

        "category":
            category

    }


    # Disable buttons

    view = CategoryView(

        interaction.user

    )


    for item in view.children:

        item.disabled = True


    # Edit category message

    await interaction.response.edit_message(

        content="🎮 Starting game...",

        view=view

    )


    # Create embed

    embed = discord.Embed(

        title="🎮 Emoji Guessing Game",

        description=

            f"Category: **{category.title()}**\n\n"
            f"# {emojis}\n\n"
            f"⏱️ You have **{GAME_TIME} seconds**!\n\n"
            f"💬 Everyone can guess in chat!",

    )


    game_message = await interaction.channel.send(

        embed=embed

    )


        # ========================================
    # WAIT FOR ANSWER
    # ========================================

    def check(message):

        return (

            message.channel.id == channel_id

            and

            not message.author.bot

        )


       # ========================================
    # COUNTDOWN
    # ========================================

    async def countdown():

        remaining = GAME_TIME


        while remaining > 0:

            await asyncio.sleep(10)

            remaining -= 10


            # ====================================
            # 30 SECOND HINT
            # ====================================

            if remaining == 30:

                answer = answers[0]

                hint = generate_hint(
                    answer
                )


                letter_count = len(

                    [
                        character

                        for character in answer

                        if character.isalpha()
                    ]

                )


                await interaction.channel.send(

                    f"💡 **HINT!** 👀\n\n"

                    f"`{hint}`\n\n"

                    f"📝 Total letters: **{letter_count}**"

                )


            # ====================================
            # COUNTDOWN MESSAGE
            # ====================================

            if remaining > 0:

                await interaction.channel.send(

                    f"⏱️ **{remaining} seconds remaining!**"

                )


       # ========================================
    # START COUNTDOWN
    # ========================================

    countdown_task = asyncio.create_task(
        countdown()
    )


    # ========================================
    # GAME TIMER
    # ========================================

    start_time = asyncio.get_event_loop().time()


    try:

        while True:

            elapsed = (
                asyncio.get_event_loop().time()
                - start_time
            )


            remaining_time = (
                GAME_TIME
                - elapsed
            )


            if remaining_time <= 0:

                raise asyncio.TimeoutError


            message = await interaction.client.wait_for(

                "message",

                timeout=remaining_time,

                check=check

            )


            # ====================================
            # CORRECT ANSWER
            # ====================================

            if check_answer(

                message.content,

                answers

            ):


                # Stop countdown

                countdown_task.cancel()


                score = add_score(

                    message.author

                )


                winner_embed = discord.Embed(

                    title="🎉 Correct!",

                    description=(

                        f"🏆 {message.author.mention} "
                        f"got it!\n\n"

                        f"✅ Answer: **{answers[0]}**\n\n"

                        f"⭐ Total Score: **{score}**"

                    )

                )


                await interaction.channel.send(

                    embed=winner_embed

                )


                break


    # ========================================
    # TIME'S UP
    # ========================================

    except asyncio.TimeoutError:


        countdown_task.cancel()


        timeout_embed = discord.Embed(

            title="⏰ Time's Up!",

            description=(

                f"The answer was:\n\n"

                f"**{answers[0]}**"

            )

        )


        await interaction.channel.send(

            embed=timeout_embed

        )


    # ========================================
    # CLEANUP
    # ========================================

    finally:


        countdown_task.cancel()


        active_games.pop(

            channel_id,

            None

        )

# ========================================
# SETUP COMMANDS
# ========================================

def setup_emoji_game(bot):


    # ====================================
    # EMOJI COMMAND
    # ====================================

    @bot.tree.command(

        name="emoji",

        description="Start an emoji guessing game!"

    )
    async def emoji(

        interaction: discord.Interaction

    ):


        channel_id = interaction.channel.id


        # Check active game

        if channel_id in active_games:

            await interaction.response.send_message(

                "❌ There is already an active emoji game in this channel!",

                ephemeral=True

            )

            return


        # Category embed

        embed = discord.Embed(

            title="🎮 Emoji Guessing Game",

            description=

                "Choose a category to start!\n\n"

                "🎬 **Movies**\n"

                "🍥 **Anime**\n"

                "🌍 **Countries**\n"

                "💬 **Words**"

        )


        view = CategoryView(

            interaction.user

        )


        await interaction.response.send_message(

            embed=embed,

            view=view

        )


    # ====================================
    # HIGHSCORE COMMAND
    # ====================================

    @bot.tree.command(

        name="emoji_highscore",

        description="View the emoji game highscore!"

    )
    async def emoji_highscore(

        interaction: discord.Interaction

    ):


        scores = load_scores()


        if not scores:

            await interaction.response.send_message(

                "🏆 No scores yet! Be the first to win an emoji game!"

            )

            return


        # Sort scores

        sorted_scores = sorted(

            scores.values(),

            key=lambda item:

                item["score"],

            reverse=True

        )


        # Create leaderboard

        leaderboard = []


        for index, player in enumerate(

            sorted_scores[:10],

            start=1

        ):


            leaderboard.append(

                f"**{index}.** "
                f"{player['name']} — "
                f"🏆 {player['score']}"

            )


        embed = discord.Embed(

            title="🏆 Emoji Game Highscores",

            description="\n".join(

                leaderboard

            )

        )


        await interaction.response.send_message(

            embed=embed

        )
