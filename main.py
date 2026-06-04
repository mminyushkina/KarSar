"""
Simple Telegram bot that replies with random text from Answers.txt
Hosted on bothost.ru
Features per-user in-memory seen-message cache,
reset after 50 unique messages shown.
"""

import os
import random
import logging

from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message
from aiogram import F

# Load .env
load_dotenv()

# Logging
logging.basicConfig(level=logging.INFO)

# Config
BOT_TOKEN = (
    os.getenv("BOT_TOKEN")
    or os.getenv("API_TOKEN")
    or os.getenv("TELEGRAM_BOT_TOKEN")
)

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN not found in .env")

ANSWERS_FILE = "Answers.txt"
CACHE_RESET_THRESHOLD = 50


def load_answers() -> list[str]:
    """Load answers from file, split by '===' separator."""
    if not os.path.exists(ANSWERS_FILE):
        logging.warning(f"{ANSWERS_FILE} not found, using fallback")
        return ["Привет! Помолчим."]

    with open(ANSWERS_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    answers = [chunk.strip() for chunk in content.split("===") if chunk.strip()]
    return answers if answers else ["Ответов пока нет."]


# Init bot
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

answers: list[str] = []

# Per-user cache: user_id -> set of seen answer indices
seen_cache: dict[int, set[int]] = {}


@dp.message(Command("start"))
async def cmd_start(message: Message) -> None:
    await message.answer(
        "Привет! Ну, рассказывай..."
    )


@dp.message(F.text)
async def random_answer(message: Message) -> None:
    global answers, seen_cache

    if not answers:
        answers = load_answers()

    user_id = message.from_user.id

    # Get or create seen set for this user
    seen = seen_cache.get(user_id)

    # If user has no cache yet, initialise with empty set
    if seen is None:
        seen = set()
        seen_cache[user_id] = seen

    # Determine available (unseen) indices
    all_indices = set(range(len(answers)))
    unseen = all_indices - seen

    # If all answers have been seen, reset the cache
    if not unseen:
        logging.info(
            f"User {user_id} has seen all {len(seen)} answers, resetting cache"
        )
        seen.clear()
        unseen = all_indices

    # Pick a random unseen answer
    chosen_index = random.choice(list(unseen))
    seen.add(chosen_index)

    # If threshold reached, reset cache for this user
    if len(seen) >= CACHE_RESET_THRESHOLD:
        logging.info(
            f"User {user_id} reached {CACHE_RESET_THRESHOLD} seen messages, "
            f"resetting cache"
        )
        seen.clear()

    reply = answers[chosen_index]
    await message.answer(reply)


async def main() -> None:
    global answers
    answers = load_answers()
    logging.info(f"Loaded {len(answers)} answers")
    logging.info("Bot started. Press Ctrl+C to stop.")
    await dp.start_polling(bot)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
