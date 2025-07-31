from telegram_notify.notify import send_message
import datetime
import argparse
import os


def notification(job_status, command):
    date = datetime.datetime.now().strftime("%T %h %d %Z")
    hostname = os.uname()[1]

    message = (
        f"*Notification:{job_status}\\!*\n"
        + f"*Job:* `{command}`\n"
        + f"*Host:* `{hostname}`\n"
        + f"*Time:* {date}"
    )
    send_message(message)


def initiate_command(command):
    notification("Job Started", command)
    if os.system(command):
        notification("Job Failed", command)
    else:
        notification("Job Finished", command)


def record():
    parser = argparse.ArgumentParser(
        prog="notify",
        description="messages telegram chat",
        epilog="",
    )
    parser.add_argument("command", nargs="*")
    args = parser.parse_args()
    initiate_command(" ".join(args.command))
