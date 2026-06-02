"""
Simple Telegram bot that replies with random text from Answers.txt
Hosted on bothost.ru
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


def load_answers() -> list[str]:
    """Load answers from file, split by '===' separator."""
    if not os.path.exists(ANSWERS_FILE):
        logging.warning(f"{ANSWERS_FILE} not found, using fallback")
        return ["Привет! Я пока не знаю, что ответить."]

    with open(ANSWERS_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    answers = [chunk.strip() for chunk in content.split("===") if chunk.strip()]
    return answers if answers else ["Ответов пока нет."]


# Init bot
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

answers: list[str] = []


@dp.message(Command("start"))
async def cmd_start(message: Message) -> None:
    await message.answer(
        "Привет! Я бот-цитатник. Напиши мне что-нибудь, и я отвечу случайной фразой."
    )


@dp.message(F.text)
async def random_answer(message: Message) -> None:
    global answers
    if not answers:
        answers = load_answers()
    reply = random.choice(answers)
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