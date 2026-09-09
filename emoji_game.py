import discord
import json
import os
import asyncio
import random
import re


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
# EMBED COLORS
# ========================================

CATEGORY_COLORS = {

    "movies": 0xE74C3C,

    "anime": 0x9B59B6,

    "countries": 0x2ECC71,

    "words": 0xF39C12

}


# ========================================
# CATEGORY EMOJIS
# ========================================

CATEGORY_EMOJIS = {

    "movies": "🎬",

    "anime": "🍥",

    "countries": "🌍",

    "words": "💬"

}


# ========================================
# TIMER BAR
# ========================================

def create_timer_bar(remaining):

    total_blocks = 10

    filled_blocks = int(
        (remaining / GAME_TIME)
        * total_blocks
    )


    empty_blocks = (
        total_blocks
        - filled_blocks
    )


    return (

        "🟩" * filled_blocks

        +

        "⬜" * empty_blocks

    )

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

def add_score(user):

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
# GENERATE HINT
# ========================================

def generate_hint(answer):

    words = answer.split(" ")

    hinted_words = []

    for word in words:

        if not word:

            hinted_words.append("")
            continue

        hint_word = ""

        for index, character in enumerate(word):

            if index == 0 and character.isalpha():

                hint_word += character

            elif character == "-":

                hint_word += "-"

            elif character.isalpha():

                hint_word += "_"

            else:

                hint_word += character

        hinted_words.append(
            hint_word
        )

    return " ".join(
        hinted_words
    )


# ========================================
# CREATE GAME EMBED
# ========================================

def create_game_embed(
    category,
    emojis,
    remaining,
    hint=None,
    letter_count=None
):

   embed = discord.Embed(

    title="🎮 Emoji Guessing Game",

    description=(

        "## Ready to test your brain? 🧠⚡\n\n"

        "Pick a category below and guess "
        "the answer before time runs out!\n\n"

        "━━━━━━━━━━━━━━━━━━\n\n"

        "🎬 **Movies**\n"
        "🍥 **Anime**\n"
        "🌍 **Countries**\n"
        "💬 **Words & Phrases**"

    ),

    color=0x5865F2

)


embed.set_footer(

    text="🏆 Get answers right to climb the leaderboard!"

)
    # ====================================
    # HINT FIELD
    # ====================================

    if hint:

        embed.add_field(

            name="💡 HINT",

            value=f"`{hint}`",

            inline=False

        )


        embed.add_field(

            name="📝 TOTAL LETTERS",

            value=f"**{letter_count}**",

            inline=True

        )


    return embed

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
            interaction.user.id
            != self.author.id
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
# START GAME
# ========================================

async def start_game(
    interaction,
    category
):

    channel_id = interaction.channel.id


    # ====================================
    # CHECK ACTIVE GAME
    # ====================================

    if channel_id in active_games:

        await interaction.response.send_message(

            "❌ There is already an active emoji game in this channel!",

            ephemeral=True

        )

        return


    # ====================================
    # LOAD PUZZLES
    # ====================================

    puzzles = load_json(
        PUZZLES_PATH,
        {}
    )


    # ====================================
    # CHECK CATEGORY
    # ====================================

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


    # ====================================
    # PICK PUZZLE
    # ====================================

    puzzle = random.choice(
        puzzles[category]
    )


    # Get emojis and answers from puzzles.json

    emojis = puzzle[
        "emojis"
    ]


    answers = puzzle[
        "answers"
    ]


    # ====================================
    # REGISTER GAME
    # ====================================

    active_games[channel_id] = {

        "answers": answers,

        "category": category

    }


    # ====================================
    # DISABLE CATEGORY BUTTONS
    # ====================================

    view = CategoryView(
        interaction.user
    )


    for item in view.children:

        item.disabled = True


    await interaction.response.edit_message(

        content="🎮 Starting game...",

        view=view

    )


    # ====================================
    # CREATE GAME EMBED
    # ====================================

    ecategory_emoji = CATEGORY_EMOJIS.get(

    category,

    "🎮"

)


category_color = CATEGORY_COLORS.get(

    category,

    0x5865F2

)


embed = discord.Embed(

    title=f"{category_emoji} EMOJI CHALLENGE!",

    description=(

        f"### {category.title()}\n\n"

        f"# {emojis}\n\n"

        "━━━━━━━━━━━━━━━━━━\n\n"

        f"⏳ **Time Remaining: {GAME_TIME}s**\n"

        f"{create_timer_bar(GAME_TIME)}\n\n"

        "💬 **Type your guess in chat!**\n"

        "🏆 First correct answer wins!"

    ),

    color=category_color

)


embed.set_footer(

    text="🔥 Think fast • Guess faster"

)


    # ====================================
    # MESSAGE CHECK
    # ====================================

    def check(message):

        return (

            message.channel.id == channel_id

            and

            not message.author.bot

        )


    # ====================================
    # UPDATE TIMER EMBED
    # ====================================

    async def countdown():

        remaining = GAME_TIME

        hint_shown = False


        while remaining > 0:

            await asyncio.sleep(5)

            remaining -= 5


            # ================================
            # CREATE UPDATED EMBED
            # ================================

           updated_embed = discord.Embed(

    title=f"{category_emoji} EMOJI CHALLENGE!",

    description=(

        f"### {category.title()}\n\n"

        f"# {emojis}\n\n"

        "━━━━━━━━━━━━━━━━━━\n\n"

        f"⏳ **Time Remaining: {remaining}s**\n"

        f"{create_timer_bar(remaining)}\n\n"

        "💬 **Type your guess in chat!**\n"

        "🏆 First correct answer wins!"

    ),

    color=category_color

)


updated_embed.set_footer(

    text="🔥 Think fast • Guess faster"

)

            # ================================
            # 30 SECOND HINT
            # ================================

            if remaining <= 30 and not hint_shown:

                hint_shown = True


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


               updated_embed.add_field(

    name="💡 HINT UNLOCKED! 👀",

    value=(

        f"## `{hint}`\n\n"

        f"🔤 **Letters:** {letter_count}\n"

        "💭 *Use your brain... or your friends!*"

    ),

    inline=False

)


            # ================================
            # EDIT GAME EMBED
            # ================================

            if remaining > 0:

                await game_message.edit(

                    embed=updated_embed

                )


    # ====================================
    # START COUNTDOWN
    # ====================================

    countdown_task = asyncio.create_task(

        countdown()

    )


    # ====================================
    # GAME TIMER
    # ====================================

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


            # ================================
            # CORRECT ANSWER
            # ================================

            if check_answer(

                message.content,

                answers

            ):


                # Cancel countdown

                countdown_task.cancel()


                # Add score

                score = add_score(

                    message.author

                )


                # Correct answer embed

              winner_embed = discord.Embed(

    title="🎉 WE HAVE A WINNER! 🎉",

    description=(

        f"## 🏆 {message.author.mention}\n\n"

        "━━━━━━━━━━━━━━━━━━\n\n"

        f"🎯 **Correct Answer**\n"
        f"## {answers[0]}\n\n"

        f"⭐ **Total Score:** {score}\n\n"

        "🔥 *Can anyone stop them?*"

    ),

    color=0xF1C40F

)


winner_embed.set_footer(

    text="🏆 Check /emoji_highscore to see the rankings!"

)

                await interaction.channel.send(

                    embed=winner_embed

                )


                break


    # ====================================
    # TIME'S UP
    # ====================================

    except asyncio.TimeoutError:


        countdown_task.cancel()


      timeout_embed = discord.Embed(

    title="⏰ TIME'S UP!",

    description=(

        "Nobody got it this time... 😭\n\n"

        "━━━━━━━━━━━━━━━━━━\n\n"

        "🎯 **The answer was:**\n"

        f"## {answers[0]}\n\n"

        "💀 Better luck next round!"

    ),

    color=0xE74C3C

)


timeout_embed.set_footer(

    text="🎮 Start another game with /emoji"

)


        await interaction.channel.send(

            embed=timeout_embed

        )


    # ====================================
    # CLEANUP
    # ====================================

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


        if channel_id in active_games:

            await interaction.response.send_message(

                "❌ There is already an active emoji game in this channel!",

                ephemeral=True

            )

            return


        # ====================================
        # CATEGORY EMBED
        # ====================================

        embed = discord.Embed(

            title="🎮 Emoji Guessing Game",

            description=(

                "Choose a category to start!\n\n"

                "🎬 **Movies**\n"

                "🍥 **Anime**\n"

                "🌍 **Countries**\n"

                "💬 **Words**"

            )

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


        # ====================================
        # SORT SCORES
        # ====================================

        sorted_scores = sorted(

            scores.values(),

            key=lambda item:
                item["score"],

            reverse=True

        )


              # ====================================
        # CREATE LEADERBOARD
        # ====================================

        leaderboard = []


        for index, player in enumerate(

            sorted_scores[:10],

            start=1

        ):


            # Medal emojis for top 3

            if index == 1:

                medal = "🥇"


            elif index == 2:

                medal = "🥈"


            elif index == 3:

                medal = "🥉"


            else:

                medal = f"`#{index}`"


            leaderboard.append(

                f"{medal} **{player['name']}**\n"

                f"　🏆 **{player['score']} points**"

            )


        # ====================================
        # CREATE COLORFUL EMBED
        # ====================================

        embed = discord.Embed(

            title="🏆 EMOJI GAME LEADERBOARD 🏆",

            description=(

                "🔥 **Who is the Emoji Master?** 🔥\n\n"

                + "\n\n".join(leaderboard)

            ),

            color=discord.Color.gold()

        )


        # Footer

        embed.set_footer(

            text="🎮 Keep playing to climb the leaderboard!"

        )


        # ====================================
        # SEND LEADERBOARD
        # ====================================

        await interaction.response.send_message(

            embed=embed

        )
