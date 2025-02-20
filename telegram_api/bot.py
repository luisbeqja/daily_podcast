import asyncio
import logging
import os
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ChatPermissions
from telegram.ext import (
    Application, 
    CommandHandler, 
    ContextTypes, 
    MessageHandler, 
    filters, 
    CallbackQueryHandler,
    ConversationHandler
)
from typing import Set
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from llm.llm import start_chain

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
WAITING_FOR_LANGUAGE = 3  # New state for language selection

# Set to store users who have received their episode
users_with_episode: Set[int] = set()

# Add this to store user's language preference
def get_language_name(lang_code):
    return {
        'en': 'English 🇬🇧',
        'es': 'Spanish 🇪🇸',
        'it': 'Italian 🇮🇹'
    }.get(lang_code, 'English 🇬🇧')

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


#TODO: fix this function at the moment it's return: ERROR - Failed to restrict user: Method is available only for supergroups
async def restrict_user(context: ContextTypes.DEFAULT_TYPE, user_id: int, msg) -> None:
    """Restrict a user from sending messages."""
    try:
        await context.bot.restrict_chat_member(
            chat_id=user_id,
            user_id=user_id,
            permissions=ChatPermissions(
                can_send_messages=False,
                can_send_polls=False,
                can_send_other_messages=False,
                can_add_web_page_previews=False,
                can_change_info=False,
                can_invite_users=False,
                can_pin_messages=False
            )
        )
        await msg.reply_text(
            "I've temporarily restricted messages until tomorrow's episode. "
            "Don't worry, I'll notify you when the next episode is ready! 🎙️✨"
        )
    except Exception as e:
        logger.error(f"Failed to restrict user: {e}")
        # Fallback to just using our internal tracking
        users_with_episode.add(user_id)

async def send_podcast(update: Update, context: ContextTypes.DEFAULT_TYPE, podcast_topic: str, language: str, message=None):
    """Send an existing podcast audio file to the user."""
    try:
        # Use the provided message object or try to get it from update
        msg = message or update.message
        if not msg:
            logger.error("No message object available")
            return
        
        # Pass podcast_topic instead of msg
        start_chain(podcast_topic, language)

        # Path to the audio file
        audio_path = os.path.join("llm", "episodes", f"first_episode.mp3")
        audio_path_1 = os.path.join("llm", "episodes", f"episode_1.mp3")
        
        # Check if file exists
        if os.path.exists(audio_path):
            # Send the audio file
            await msg.reply_text("🎙️ Here's your podcast, enjoy!")
            await msg.reply_audio(
                audio=open(audio_path, 'rb'),
                title=f"Introduction on {podcast_topic}",
                filename=f"Introduction {podcast_topic.replace(' ', '_')}.mp3"
            )
            await msg.reply_audio(
                audio=open(audio_path_1, 'rb'),
                title=f"First Episode about {audio_path_1}",
                caption="There you go! this is the first episode of your podcast! Tomorrow you will receive the next one! 🎧",
                filename=f"First Episode {audio_path_1.replace(' ', '_')}.mp3"
            )
            
            # Get user ID and restrict them
            user_id = msg.chat.id
            users_with_episode.add(user_id)
            
            # Restrict user from sending messages
            await restrict_user(context, user_id, msg)
                
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
    elif query.data.startswith('lang_'):
        # Handle language selection
        language = query.data.split('_')[1]
        context.user_data['language'] = language
        
        # Create confirmation buttons
        keyboard = [
            [
                InlineKeyboardButton("Yes ✅", callback_data='confirm_yes'),
                InlineKeyboardButton("No, change topic ❌", callback_data='confirm_no')
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.message.reply_text(
            f"You selected {get_language_name(language)}.\n"
            f"Would you like me to generate the podcast now?",
            reply_markup=reply_markup
        )
        return WAITING_FOR_CONFIRMATION
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
        
        # Get the topic and language from user data and generate/send the podcast
        podcast_topic = context.user_data.get('podcast_topic')
        language = context.user_data.get('language', 'en')  # default to English
        if podcast_topic:
            await send_podcast(update, context, podcast_topic, language, message=query.message)
        else:
            await query.message.reply_text("Sorry, I couldn't find your podcast topic. Please try again.")
        
        return ConversationHandler.END
    elif query.data == 'confirm_no':
        await query.message.reply_text("No problem! Please tell me a different topic you'd like to hear about 🎙️")
        return WAITING_FOR_TOPIC

async def check_user_restriction(update: Update) -> bool:
    """Check if user is allowed to send messages."""
    user_id = update.effective_user.id
    if user_id in users_with_episode:
        await update.message.reply_text(
            "You've already received today's episode! 🎙️\n"
            "Please wait for tomorrow's episode. I'll notify you when it's ready! ✨"
        )
        return False
    return True

async def receive_topic(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle the podcast topic input."""
    # Check if user is allowed to send messages
    if not await check_user_restriction(update):
        return ConversationHandler.END
        
    podcast_topic = update.message.text
    context.user_data['podcast_topic'] = podcast_topic
    
    # Create language selection buttons
    keyboard = [
        [
            InlineKeyboardButton("English 🇬🇧", callback_data='lang_en'),
            InlineKeyboardButton("Spanish 🇪🇸", callback_data='lang_es'),
            InlineKeyboardButton("Italian 🇮🇹", callback_data='lang_it')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"Great! I'll create a podcast about: '{podcast_topic}' 🎙️\n"
        "In which language would you like to listen to it?",
        reply_markup=reply_markup
    )
    
    logger.info(f"Received podcast topic: {podcast_topic}")
    return WAITING_FOR_LANGUAGE

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

    # Create conversation handler with the new language selection state
    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler("start", start),
            CallbackQueryHandler(button_callback)
        ],
        states={
            WAITING_FOR_TOPIC: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_topic)],
            WAITING_FOR_LANGUAGE: [CallbackQueryHandler(button_callback)],
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