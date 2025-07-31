import requests
import argparse
import os


def send_message(
    message: str, parse_mode: str = "MarkdownV2", bot_id=None, chat_id=None
):
    if bot_id is None:
        bot_id = os.environ["TELEGRAM_BOT_ID"]
    if chat_id is None:
        chat_id = os.environ["TELEGRAM_CHAT_ID"]
    try:
        requests.post(
            f"https://api.telegram.org/bot{bot_id}/sendMessage?chat_id={chat_id}&parse_mode={parse_mode}&text={message.replace('\\n', '\n')}"
        )
        return 0
    except Exception:
        return 1


def notify():
    parser = argparse.ArgumentParser(
        prog="notify",
        description="messages telegram chat",
        epilog="",
    )
    parser.add_argument("-b", "--bot_id")
    parser.add_argument("-c", "--chat_id")
    parser.add_argument("-p", "--parse_mode")
    parser.add_argument("message")
    args = parser.parse_args()
    send_message(args.message, args.bot_id, args.chat_id, args.parse_mode)
