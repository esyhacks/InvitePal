import os
import re
import logging
import mysql.connector
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.error import TelegramError
from telegram.ext import (ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters)

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Bot token, username, and target channel from environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
BOT_USERNAME = os.getenv("BOT_USERNAME")
TARGET_CHANNEL = os.getenv("TARGET_CHANNEL")

# Sticker IDs
STICKER_ID = os.getenv("STICKER_ID")
STICKER_ID_2 = os.getenv("STICKER_ID_2")
STICKER_ID_3 = os.getenv("STICKER_ID_3")
STICKER_ID_4 = os.getenv("STICKER_ID_4")
STICKER_ID_5 = os.getenv("STICKER_ID_5")

# Configure logging
logging.basicConfig(format='[%(levelname)s] %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)
logging.getLogger("httpx").setLevel(logging.CRITICAL)
logging.getLogger("telegram").setLevel(logging.CRITICAL)

# Database configuration from environment variables
DB_CONFIG = {
    'host': os.getenv("DB_HOST"),
    'user': os.getenv("DB_USER"),
    'port': os.getenv("DB_PORT"),
    'password': os.getenv("DB_PASSWORD"),
    'database': os.getenv("DB_NAME")
}

def get_db_connection():
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except Exception as e:
        logger.error("Could not connect to the database.")
        raise

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = update.effective_user.id
        username = update.effective_user.username or "Unknown"
        referred_by = int(context.args[0]) if context.args and context.args[0].isdigit() else None

        logger.info(f"Processing /start command for user {user_id} (@{username})")

        # Check if user is in the channel
        is_member = await context.bot.get_chat_member(TARGET_CHANNEL, user_id)
        joined = is_member.status in ["member", "administrator", "creator"]

        conn = get_db_connection()
        cursor = conn.cursor()

        # Query user data from the database
        cursor.execute("SELECT is_joined, referred_by, points_credited FROM Users WHERE telegram_id = %s", (user_id,))
        result = cursor.fetchone()

        if result:
            is_joined_db, db_referred_by, points_credited = result

            if joined:
                if not is_joined_db:
                    cursor.execute("UPDATE Users SET is_joined = TRUE WHERE telegram_id = %s", (user_id,))
                    conn.commit()
                    logger.info(f"Updated is_joined status to TRUE for user {user_id}")

                    # Credit points to the referrer only if not credited before
                    if db_referred_by and db_referred_by != user_id and not points_credited:
                        cursor.execute("UPDATE Users SET points_available = points_available + 10 WHERE telegram_id = %s", (db_referred_by,))
                        cursor.execute("UPDATE Users SET points_credited = TRUE WHERE telegram_id = %s", (user_id,))
                        conn.commit()
                        logger.info(f"Incremented points for referrer {db_referred_by} due to referral by {user_id}")
                        await context.bot.send_sticker(chat_id=db_referred_by, sticker=STICKER_ID_2)
                        await context.bot.send_message(chat_id=db_referred_by, text=f"*Good news! {update.effective_user.first_name} is with us now.*\nI've given you *10 points* for bringing them in. Keep it up!", parse_mode ="Markdown")
                await display_menu(update, context)
            else:
                cursor.execute("UPDATE Users SET is_joined = FALSE WHERE telegram_id = %s", (user_id,))
                conn.commit()
                logger.warning(f"User {user_id} not joined the channel. Prompting to join.")
                await prompt_join_channel(update, context)
        else:
            # Insert new user into the database
            cursor.execute(
                "INSERT INTO Users (telegram_id, username, referred_by, is_joined, points_credited) VALUES (%s, %s, %s, %s, %s)",
                (user_id, username, referred_by if referred_by and referred_by != user_id else None, joined, False),
            )
            conn.commit()
            logger.info(f"New user {user_id} added to the database.")

            if joined:
                await display_menu(update, context)
            else:
                logger.warning(f"New user {user_id} not joined the channel. Prompting to join.")
                await prompt_join_channel(update, context)

        cursor.close()
        conn.close()

    except Exception as e:
        logger.error(f"An error occurred in /start command: {e}")

def channel_membership_required(func):
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        try:
            user_id = update.effective_user.id
            is_member = await context.bot.get_chat_member(TARGET_CHANNEL, user_id)
            if is_member.status in ["member", "administrator", "creator"]:
                return await func(update, context, *args, **kwargs)
            else:
                await prompt_join_channel(update, context)
        except Exception as e:
            logger.error(f"Error in channel_membership_required for user {user_id}: {e}")
    return wrapper

async def display_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        logger.info(f"Displaying menu for user {update.effective_user.id}")
        keyboard = [
            [InlineKeyboardButton("List Rewards", callback_data="rewards"),
             InlineKeyboardButton("Get Referral Link", callback_data="referral_link")],
            [InlineKeyboardButton("My Referrals", callback_data="referrals"),
             InlineKeyboardButton("My Balance", callback_data="balance")],
            [InlineKeyboardButton("Redeem Rewards", callback_data="redeem"),
             InlineKeyboardButton("Get Help", callback_data="help")]
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)
        await context.bot.send_sticker(chat_id=update.effective_chat.id, sticker=STICKER_ID_3)
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"*Hello {update.effective_user.first_name}!*\nSelect what you want me to do:", parse_mode="Markdown", reply_markup=reply_markup)
    except Exception as e:
        logger.error(f"Error in display_menu for user {update.effective_user.id}: {e}")

async def prompt_join_channel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="*Please join our channel to use this feature.\nOnce joined, press /start again.*",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("Join Channel", url=f"https://t.me/{TARGET_CHANNEL[1:]}")]]
            )
        )
    except Exception as e:
        logger.error(f"Error in prompt_join_channel for user {update.effective_user.id}: {e}")

def escape_md(text):
    # Escape all special MarkdownV2 characters
    special_chars = r"_*[]()~`>#+-=|{}.!"
    return re.sub(f"([{re.escape(special_chars)}])", r"\\\1", text)

@channel_membership_required
async def fallback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = update.effective_user.id
        logger.info(f"Unknown message received from user {user_id}: {update.message.text}")
        
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=(
                "🤔 *I'm not sure what you meant by that.*"
            ),
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.error(f"Error in fallback handler for user {update.effective_user.id}: {e}")

@channel_membership_required
async def handle_rewards(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        logger.info(f"Fetching rewards for user {update.effective_user.id}")
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT item_id, item_description, points_required, redeemed_count, max_count FROM Rewards")
        rewards = cursor.fetchall()

        if not rewards:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="*No rewards available at the moment.*", parse_mode="Markdown")
            return

        for reward in rewards:
            item_id, item_description, points_required, redeemed_count, max_count = reward

            # Calculate available slots
            slots_available = max_count - redeemed_count

            # Prepare the message for each reward
            message = (
                f"*Item ID:* {item_id}\n"
                f"*Name: {item_description}*\n"
                f"*Slots: {slots_available}* out of {max_count} available\n"
                f"*Points Required:* {points_required}"
            )

            await context.bot.send_message(chat_id=update.effective_chat.id, text=message, parse_mode="Markdown")
        await context.bot.send_message(chat_id=update.effective_chat.id, text="*When you have enough points, you can redeem any item above ☝️ at anytime.\n I'm here to serve you 24x7 😎*", parse_mode="Markdown")
        logger.info(f"Sent reward details to user {update.effective_user.id}")

    except Exception as e:
        logger.error(f"Error in handle_rewards for user {update.effective_user.id}: {e}")
    finally:
        cursor.close()
        conn.close()

@channel_membership_required
async def get_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = update.effective_user.id
        link = f"https://t.me/{BOT_USERNAME}?start={user_id}"
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"*Your referral link:\n{link}*", parse_mode="Markdown")
        await context.bot.send_sticker(chat_id=update.effective_chat.id, sticker=STICKER_ID_4)
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"*Share among your friends, {update.effective_user.first_name}!*", parse_mode="Markdown")
        logger.info(f"Sent referral link to user {user_id}")
    except Exception as e:
        logger.error(f"Error in get_link for user {update.effective_user.id}: {e}")

@channel_membership_required
async def referrals(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = update.effective_user.id
        logger.info(f"Fetching referrals for user {user_id}")

        conn = get_db_connection()
        cursor = conn.cursor()

        # Fetch Telegram IDs from the database
        cursor.execute("SELECT telegram_id FROM Users WHERE referred_by = %s", (user_id,))
        referrals = cursor.fetchall()

        # Initialize the message
        if referrals:
            message = "*Friends who have joined us:*\n\n"
            for referral in referrals:
                telegram_id = referral[0]
                try:
                    # Fetch user details using the Telegram API
                    user = await context.bot.get_chat(telegram_id)
                    full_name = f"{user.first_name} {user.last_name}" if user.last_name else user.first_name
                    username = f"@{user.username}" if user.username else "no username"
                    message += f"*- {full_name} ({username})*\n"
                except Exception as e:
                    # Handle cases where the Telegram ID is invalid or user info is not accessible
                    logger.error(f"Could not fetch details for Telegram ID {telegram_id}: {e}")
                    message += f"*- Telegram ID: {telegram_id} (details not available)*\n"
        else:
            message = "*Hmm... Seems like we need more people here.*"

        await context.bot.send_message(chat_id=update.effective_chat.id, text=message, parse_mode="Markdown")
        logger.info(f"Sent referrals list to user {user_id}")

    except Exception as e:
        logger.error(f"Error in referrals for user {user_id}: {e}")
    finally:
        cursor.close()
        conn.close()

@channel_membership_required
async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = update.effective_user.id
        logger.info(f"Fetching balance for user {user_id}")

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT points_available FROM Users WHERE telegram_id = %s", (user_id,))
        points = cursor.fetchone()[0]

        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"*You have a balance of ||{escape_md(f'{points} points.')}||*", parse_mode="MarkdownV2")
        logger.info(f"Sent balance to user {user_id}")

    except Exception as e:
        logger.error(f"Error in balance for user {user_id}: {e}")
    finally:
        cursor.close()
        conn.close()

@channel_membership_required
async def redeem(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if len(context.args) != 1:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="*This is the syntax you must follow:\n/redeem <item-id>*", parse_mode="Markdown")
            logger.warning(f"Invalid redeem usage by user {update.effective_user.id}")
            return

        item_id = context.args[0]
        user_id = update.effective_user.id
        logger.info(f"Processing redeem request for user {user_id}, item {item_id}")

        conn = get_db_connection()
        cursor = conn.cursor()

        # Fetch user points
        cursor.execute("SELECT points_available FROM Users WHERE telegram_id = %s", (user_id,))
        user_data = cursor.fetchone()
        if not user_data:
            logger.error(f"User {user_id} not found in database.")
            return

        points = user_data[0]

        # Fetch reward details
        cursor.execute("SELECT item_description, points_required, secret_1, secret_2, redeemed_count, max_count FROM Rewards WHERE item_id = %s", (item_id,))
        reward = cursor.fetchone()

        if not reward:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="*Sorry, item id seems to be incorrect.*", parse_mode="Markdown")
            logger.error(f"Invalid reward ID {item_id} for user {user_id}")
            return

        item_description, points_required, secret_1, secret_2, redeemed_count, max_count = reward

        # Check if reward is still available
        if redeemed_count >= max_count:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="*Sorry, This reward is no longer available.*", parse_mode="Markdown")
            logger.warning(f"Reward {item_id} has reached its redemption limit.")
            return

        # Check if user has enough points
        if points < points_required:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="*Sorry, You don't have enough points to redeem this item.*", parse_mode="Markdown")
            logger.warning(f"User {user_id} attempted to redeem {item_id} with insufficient points")
            return

        # Deduct points and update redemption count
        cursor.execute(
            "UPDATE Users SET points_available = points_available - %s WHERE telegram_id = %s",
            (points_required, user_id)
        )
        cursor.execute(
            "UPDATE Rewards SET redeemed_count = redeemed_count + 1 WHERE item_id = %s",
            (item_id,)
        )
        conn.commit()

        await context.bot.send_sticker(chat_id=update.effective_chat.id, sticker=STICKER_ID_5)
        await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=(
            f"*Reward redeemed:\n{escape_md(item_description)}*\n\n"
            f"*Credentials:*\n"
            f"||{escape_md(secret_1)}||\n"
            f"||{escape_md(secret_2)}||"
        ),
        parse_mode="MarkdownV2"
        )
        logger.info(f"User {user_id} redeemed reward {item_id}")

    except Exception as e:
        logger.error(f"Error in redeem for user {update.effective_user.id}: {e}")
    finally:
        cursor.close()
        conn.close()

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        logger.info(f"Sending help message to user {update.effective_user.id}")
        
        # Sending a sticker (replace with your sticker ID)
        await context.bot.send_sticker(chat_id=update.effective_chat.id, sticker=STICKER_ID)
        
        # Sending a brief description about the bot
        description = (
            "👋 *Hello there!*\n\n"
            "I’m *InvitePal*, your partner in earning amazing rewards effortlessly."
            " *Ready for a deal that’s as simple as it gets?*\n\n"
            "✨ *Here’s how it works:*\n\n"
            "1️⃣ Share a special link with your friends.\n"
            "2️⃣ For every friend who joins through your link, you earn *10 reward points*.\n"
            "3️⃣ Use those points to unlock *premium online accounts completely free!* 🎉\n\n"
            "💡 *No payment collected - just rewards for sharing.*\n\n"
            "🔥 *What’s next?*\n\n"
            "- Tap the *menu button* to see all the commands I understand.\n"
            "- Hit *Start* to explore your options.\n\n"
            "🚀 I’ll handle the rest for you!\n\n"
            "⚡ *Instant rewards are ready to claim as soon as you’ve earned them.*"
            " Don’t wait - let’s get you started on earning big today! 💎"
        )

        # Adding buttons below the help message
        keyboard = [
            [InlineKeyboardButton("Submit Feedback", url="https://t.me/geobrook")],
            [InlineKeyboardButton("See me at GitHub", url="https://github.com/esyhacks/InvitePal")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        # Send the message with the description and buttons
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=description,
            parse_mode="Markdown",
            reply_markup=reply_markup
        )
        
        logger.info(f"Help message sent to user {update.effective_user.id}")
    except Exception as e:
        logger.error(f"Error in help_command for user {update.effective_user.id}: {e}", exc_info=True)

async def handle_menu_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        query = update.callback_query
        await query.answer()  # Acknowledge the button press
        user_id = update.effective_user.id
        logger.info(f"User {user_id} selected menu option: {query.data}")

        # Route based on callback_data
        if query.data == "rewards":
            await handle_rewards(update, context)
        elif query.data == "referral_link":
            await get_link(update, context)
        elif query.data == "referrals":
            await referrals(update, context)
        elif query.data == "balance":
            await balance(update, context)
        elif query.data == "redeem":
            await context.bot.send_message(chat_id=update.effective_chat.id, text="*Use /redeem <item-id> to redeem a reward.*", parse_mode="Markdown")
        elif query.data == "help":
            await help_command(update, context)
        else:
            await query.edit_message_text(text="Invalid option. Please try again.")
    except Exception as e:
        logger.error(f"Error in handle_menu_selection for user {update.effective_user.id}: {e}")
        await update.callback_query.message.reply_text("An error occurred while processing your selection. Please try again later.")

# Update main entry point to include the callback query handler
if __name__ == "__main__":
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    # Command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("rewards", channel_membership_required(handle_rewards)))
    application.add_handler(CommandHandler("get_link", channel_membership_required(get_link)))
    application.add_handler(CommandHandler("referrals", channel_membership_required(referrals)))
    application.add_handler(CommandHandler("balance", channel_membership_required(balance)))
    application.add_handler(CommandHandler("redeem", channel_membership_required(redeem)))
    application.add_handler(CommandHandler("help", help_command))

    # Callback query handler for menu buttons
    application.add_handler(CallbackQueryHandler(handle_menu_selection))

    # Fallback handler for unknown messages
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, fallback))

    logger.info("Bot started.")

    # Catch all runtime errors and display a custom message
    try:
        application.run_polling()
    except TelegramError as te:
        logger.error(f"A Telegram API error occurred: {te}")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
    finally:
        logger.info("Bot stopped.")
