import asyncio
import logging
import os
from dotenv import load_dotenv
from telegram import ForceReply, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, 
    CommandHandler, 
    ContextTypes, 
    MessageHandler, 
    filters, 
    CallbackQueryHandler,
    ConversationHandler
)

# Load environment variables
load_dotenv()

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

# Get token from environment variables
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
if not TOKEN:
    raise ValueError("No TELEGRAM_BOT_TOKEN found in environment variables")

print(TOKEN)

# Define conversation states
WAITING_FOR_TOPIC = 1
WAITING_FOR_CONFIRMATION = 2

first_message = """
Hi! I'm Lisa, your personal Podcaster 🎙️.
You can ask me to create a podcast for you based on a topic or a question.

What would you like to listen about?🧐
"""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    keyboard = [
        [
            InlineKeyboardButton("Create New Podcast 🎙️", callback_data='create_podcast'),
            InlineKeyboardButton("My Podcasts 📚", callback_data='my_podcasts')
        ],
        [InlineKeyboardButton("Help ❓", callback_data='help')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_html(
        first_message,
        reply_markup=reply_markup
    )

async def send_podcast(update: Update, context: ContextTypes.DEFAULT_TYPE, podcast_topic: str, message=None):
    """Send an existing podcast audio file to the user."""
    try:
        # Use the provided message object or try to get it from update
        msg = message or update.message
        if not msg:
            logger.error("No message object available")
            return

        # Path to the audio file
        # audio_path = os.path.join("llm", "episodes", f"{podcast_topic.replace(' ', '_')}.mp3")
        audio_path = os.path.join("llm", "episodes", f"first_episode.mp3")
        # Check if file exists
        if os.path.exists(audio_path):
            # Send the audio file
            await msg.reply_text("🎙️ Here's your podcast, enjoy!")
            await msg.reply_audio(
                audio=open(audio_path, 'rb'),
                title=f"First Episode about {podcast_topic}",
                caption="There you go! this is the first episode of your podcast! Tomorrow you will receive the next one! 🎧",
                filename=f"First Episode {podcast_topic.replace(' ', '_')}.mp3"
            )
        else:
            await msg.reply_text("Sorry, I couldn't find the podcast file. Please try a different topic. 😔")
            
    except Exception as e:
        logger.error(f"Error sending podcast: {e}")
        if msg:
            await msg.reply_text("Sorry, something went wrong while sending your podcast. Please try again later. 😔")

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle button presses."""
    query = update.callback_query
    await query.answer()

    # Delete the message with the buttons
    await query.message.delete()

    if query.data == 'create_podcast':
        await query.message.reply_text("Please tell me what topic you'd like your podcast to be about! 🎧🎧")
        return WAITING_FOR_TOPIC
    elif query.data == 'my_podcasts':
        await query.message.reply_text("Here are your previously created podcasts: (Coming soon!) 📚")
        return ConversationHandler.END
    elif query.data == 'help':
        await query.message.reply_text("I can help you create podcasts on any topic! Just tell me what you'd like to hear about. 🎧")
        return ConversationHandler.END
    elif query.data == 'confirm_yes':
        await query.message.reply_text(
            "Great! I'll start generating your podcast now!✨ "
            "It'll take some time to generate it, so please be patient. "
            "You don't have to stay on the chat, I will send you the podcast when it's ready! ❤️"
        )
        
        # Get the topic from user data and generate/send the podcast
        podcast_topic = context.user_data.get('podcast_topic')
        if podcast_topic:
            await asyncio.sleep(5)  # Add 5 second delay
            await send_podcast(update, context, podcast_topic, message=query.message)
        else:
            await query.message.reply_text("Sorry, I couldn't find your podcast topic. Please try again.")
        
        return ConversationHandler.END
    elif query.data == 'confirm_no':
        await query.message.reply_text("No problem! Please tell me a different topic you'd like to hear about 🎙️")
        return WAITING_FOR_TOPIC

async def receive_topic(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle the podcast topic input."""
    podcast_topic = update.message.text
    context.user_data['podcast_topic'] = podcast_topic
    
    # Create confirmation buttons
    keyboard = [
        [
            InlineKeyboardButton("Yes ✅", callback_data='confirm_yes'),
            InlineKeyboardButton("No, change topic ❌", callback_data='confirm_no')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"Great! I'll create a podcast about: '{podcast_topic}' 🎙️\n"
        "Would you like me to generate it now?",
        reply_markup=reply_markup
    )
    
    logger.info(f"Received podcast topic: {podcast_topic}")
    return WAITING_FOR_CONFIRMATION

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text("Help!")

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancel the conversation."""
    await update.message.reply_text("Operation cancelled. Feel free to start a new podcast anytime!")
    return ConversationHandler.END

def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(TOKEN).build()

    # Create conversation handler
    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler("start", start),
            CallbackQueryHandler(button_callback)
        ],
        states={
            WAITING_FOR_TOPIC: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_topic)],
            WAITING_FOR_CONFIRMATION: [CallbackQueryHandler(button_callback)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    # Add handlers
    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("help", help_command))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()