from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler
import datetime
import pytz

TOKEN = "Token"
WAKEUP, TIMEZONE = range(2)


def start(update, context):
    update.message.reply_text(
        "Welcome to the Water Reminder Bot! Please tell me your typical wake-up time in the format hour:minute (e.g. 07:00 for 7 AM).")
    return WAKEUP


def wakeup_time(update, context):
    context.user_data['wakeup'] = update.message.text
    update.message.reply_text(
        f"Got it! Your wake-up time is set as {update.message.text}. Now, please tell me your timezone as UTC offset (e.g. 'UTC+3' or 'UTC-4'). BA is UTC-3, and NY is UTC-4.")
    return TIMEZONE


def set_timezone(update, context):
    timezone_str = update.message.text
    try:
        print(f"Received timezone: {timezone_str}")  # Debugging
        offset_minutes = int(timezone_str.split("UTC")[-1]) * 60
        print(f"Calculated offset in minutes: {offset_minutes}")  # Debugging

        user_timezone = pytz.FixedOffset(offset_minutes)
        print(f"User timezone object: {user_timezone}")  # Debugging

        now = datetime.datetime.now(user_timezone)
        wakeup_time = datetime.datetime.strptime(
            context.user_data['wakeup'], "%H:%M").time()
        wakeup_datetime = user_timezone.localize(
            datetime.datetime.combine(now.date(), wakeup_time))
        print(f"Adjusted wakeup datetime: {wakeup_datetime}")  # Debugging

        if now.time() > wakeup_time:
            wakeup_datetime += datetime.timedelta(days=1)

        for _ in range(16):  # Assuming 16 hours of being awake
            context.job_queue.run_daily(callback=send_reminder, time=wakeup_datetime.time(
            ), context=update.message.chat_id, days=(0, 1, 2, 3, 4, 5, 6))
            # Debugging
            print(f"Scheduled reminder for: {wakeup_datetime.time()}")
            wakeup_datetime += datetime.timedelta(hours=1)

        # Schedule a test reminder 5 seconds from now
        context.job_queue.run_once(
            callback=send_reminder, when=5, context=update.message.chat_id)
        print("Test reminder scheduled for 5 seconds from now.")  # Debugging

        update.message.reply_text(
            f"Reminders set for every day, every hour from {context.user_data['wakeup']} in the {timezone_str} timezone for the next 16 hours. A test reminder will be sent in 5 seconds.")
        return ConversationHandler.END

    except Exception as e:
        print(f"Error encountered: {e}")  # Debugging
        update.message.reply_text(
            f"Sorry, I couldn't recognize the timezone '{timezone_str}'. Please provide a valid UTC offset like 'UTC+3' or 'UTC-4'.")
        return TIMEZONE


def send_reminder(context):
    job = context.job
    context.bot.send_message(job.context, text="Time to drink water!🚰")


def test_reminder(update, context):
    send_reminder(context)


def main():
    updater = Updater(token=TOKEN, use_context=True)
    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            WAKEUP: [MessageHandler(Filters.text & ~Filters.command, wakeup_time)],
            TIMEZONE: [MessageHandler(Filters.regex(
                r'^UTC[+-]\d{1,2}$'), set_timezone)]
        },
        fallbacks=[]
    )

    dp.add_handler(conv_handler)
    dp.add_handler(CommandHandler('testreminder', test_reminder))

    print("Bot started...")
    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
