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
from telegram_api.database import Database
import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from llm.llm import start_chain, start_initial_chain

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



# Define conversation states
WAITING_FOR_TOPIC = 1
WAITING_FOR_CONFIRMATION = 2
WAITING_FOR_LANGUAGE = 3  # New state for language selection
WAITING_FOR_NEXT_EPISODE = 4  # New state for next episode request

help_message = """
Heyyy! 😊 I'm Lisa, your personal Podcaster 🎙️.

You can ask me to create a podcast for you based on a topic or a question. 🤔

I will generate a podcast of 5 episodes for you. 🎧

After the first 2 episodes, I'll ask you if you want to listen to the next one. 📻

This project is still under development, so please be patient with me. 🙏

type /start to start the conversation.
"""

# Set to store users who have received their episode
users_with_episode: Set[int] = set()

# Initialize database after other global variables
db = Database()

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

async def send_podcast(update: Update, context: ContextTypes.DEFAULT_TYPE, podcast_topic: str, language: str, message=None, episode_number: int = 1):
    """Send an existing podcast audio file to the user."""
    try:
        msg = message or update.message
        if not msg:
            logger.error("No message object available")
            return
        
        # Get user information
        user_id = msg.chat.id
        username = msg.chat.username
        
        # Add user to database if not exists
        db.add_user(user_id, username)
        
        if episode_number == 1:
            # Generate first episode and intro
            start_initial_chain(podcast_topic, language, user_id, db)
        else:
            # Generate next episode
            start_chain(podcast_topic, language, user_id, db, episode_number)
        
        # Path to the audio files in user's directory
        user_dir = os.path.join("llm", "episodes", str(user_id))
        
        if episode_number == 1:
            intro_path = os.path.join(user_dir, "first_episode.mp3")
            episode_path = os.path.join(user_dir, "episode_1.mp3")
        else:
            episode_path = os.path.join(user_dir, f"episode_{episode_number}.mp3")
        
        # Store current episode number in user data
        context.user_data['current_episode'] = episode_number
        context.user_data['podcast_topic'] = podcast_topic
        context.user_data['language'] = language
        
        if episode_number == 1 and os.path.exists(intro_path) and os.path.exists(episode_path):
            # Send the audio files
            await msg.reply_text("🎙️ Here's your podcast, enjoy!")
            await msg.reply_audio(
                audio=open(intro_path, 'rb'),
                title=f"Introduction on {podcast_topic}",
                filename=f"Introduction_{podcast_topic.replace(' ', '_')}.mp3"
            )
            await msg.reply_audio(
                audio=open(episode_path, 'rb'),
                title=f"Episode {episode_number} about {podcast_topic}",
                filename=f"Episode_{episode_number}_{podcast_topic.replace(' ', '_')}.mp3"
            )
        elif episode_number > 1 and os.path.exists(episode_path):
            await msg.reply_audio(
                audio=open(episode_path, 'rb'),
                title=f"Episode {episode_number} about {podcast_topic}",
                filename=f"Episode_{episode_number}_{podcast_topic.replace(' ', '_')}.mp3"
            )
        else:
            await msg.reply_text("Sorry, I couldn't find the podcast file. Please try a different topic. 😔")
            return
            
        # Add Next Episode button if not the last episode
        if episode_number < 5:
            keyboard = [[InlineKeyboardButton("Next Episode ▶️", callback_data='next_episode')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await msg.reply_text(
                f"I hope you enjoyed Episode {episode_number}! Would you like to listen to the next episode?",
                reply_markup=reply_markup
            )
        else:
            await msg.reply_text("That was the last episode of your podcast series! I hope you enjoyed it! 🎉")
            
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
    elif query.data == 'next_episode':
        # Get the current episode number and podcast details from user data
        current_episode = context.user_data.get('current_episode', 1)
        podcast_topic = context.user_data.get('podcast_topic')
        language = context.user_data.get('language')
        
        if not all([current_episode, podcast_topic, language]):
            await query.message.reply_text("Sorry, I couldn't find your podcast information. Please start a new podcast.")
            return ConversationHandler.END
            
        # Generate and send the next episode
        next_episode = current_episode + 1
        await query.message.reply_text(f"Generating Episode {next_episode} for you! Please wait... ⏳")
        await send_podcast(update, context, podcast_topic, language, message=query.message, episode_number=next_episode)
        return WAITING_FOR_NEXT_EPISODE
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
        # Get user's podcasts from database
        user_id = query.message.chat.id
        podcasts = db.get_user_podcasts(user_id)
        
        if podcasts:
            response = "Here are your podcasts:\n\n"
            for topic, language, _, _, created_at in podcasts:
                date = datetime.datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S')
                response += f"📚 Topic: {topic}\n"
                response += f"🗣 Language: {get_language_name(language)}\n"
                response += f"📅 Created: {date.strftime('%Y-%m-%d %H:%M')}\n\n"
        else:
            response = "You haven't created any podcasts yet! 📚"
            
        await query.message.reply_text(response)
        return ConversationHandler.END
    elif query.data == 'help':
        await query.message.reply_text(help_message)
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

async def restart_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Clear user data and allow them to start fresh."""
    user_id = update.message.chat_id
    
    # Remove from restricted users set
    if user_id in users_with_episode:
        users_with_episode.remove(user_id)
    
    # Clear database entries and files
    if db.clear_user_data(user_id):
        keyboard = [
            [
                InlineKeyboardButton("Create New Podcast 🎙️", callback_data='create_podcast'),
                InlineKeyboardButton("My Podcasts 📚", callback_data='my_podcasts')
            ],
            [InlineKeyboardButton("Help ❓", callback_data='help')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "✨ All cleared! You can now create a new podcast!\n"
            "What would you like to do?",
            reply_markup=reply_markup
        )
    else:
        await update.message.reply_text(
            "Sorry, there was an error clearing your data. "
            "Please try again later or contact support."
        )

def start_bot() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(TOKEN).build()

    # Create conversation handler with the new language selection state
    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler("start", start),
            CommandHandler("restart", restart_command),
            CallbackQueryHandler(button_callback)
        ],
        states={
            WAITING_FOR_TOPIC: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_topic)],
            WAITING_FOR_LANGUAGE: [CallbackQueryHandler(button_callback)],
            WAITING_FOR_CONFIRMATION: [CallbackQueryHandler(button_callback)],
            WAITING_FOR_NEXT_EPISODE: [CallbackQueryHandler(button_callback)],
        },
        fallbacks=[
            CommandHandler("cancel", cancel),
            CommandHandler("restart", restart_command)
        ],
    )

    # Add handlers
    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("restart", restart_command))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)
