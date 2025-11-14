"""
Configuration for GSL Telegram Bot
"""
import os
from pathlib import Path

# Bot Token (get from @BotFather on Telegram)
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '8294311560:AAHmp-3UxwyUiLAeeR_t66opbaXfRXnFmg0')

# Paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / 'data'
VIDEOS_DIR = DATA_DIR / 'videos'
DICTIONARY_FILE = DATA_DIR / 'dictionary.json'

# Video categories
CATEGORIES = {
    'alphabets': VIDEOS_DIR / 'alphabets',
    'numbers': VIDEOS_DIR / 'numbers',
    'words': VIDEOS_DIR / 'words'
}

# Create directories if they don't exist
for category_dir in CATEGORIES.values():
    category_dir.mkdir(parents=True, exist_ok=True)

# Bot settings
MAX_SUGGESTIONS = 5
MAX_SEARCH_RESULTS = 5
SUPPORTED_VIDEO_FORMATS = ['.mp4', '.mov', '.avi']
SUPPORTED_IMAGE_FORMATS = ['.png', '.jpg', '.jpeg', '.gif']
ADMIN_USER_ID = None  # Set to your Telegram user ID for admin features

# Messages
WELCOME_MESSAGE = """
🇬🇭 **Welcome to GSL Dictionary Bot!**

I can help you learn Ghana Sign Language by showing you video demonstrations.

**Commands:**
/start - Show this message
/search <word> - Search for a sign (e.g., /search apple)
/alphabet - Show all alphabet signs
/numbers - Show all number signs
/categories - List all available categories
/help - Get help

**Quick searches:**
Just type any word directly (e.g., "hello", "thank you")

Let's learn GSL together! 🤟
"""

HELP_MESSAGE = """
📚 **How to use GSL Dictionary Bot:**

**1. Search for a sign:**
   • Type: `/search apple`
   • Or just: `apple`

**2. Browse by category:**
   • `/alphabet` - All letters A-Z
   • `/numbers` - Numbers 0-9
   • `/categories` - See all categories

**3. Tips:**
   • Videos show proper hand positions
   • Watch multiple times for better learning
   • Practice along with the video

Need more signs? Let us know what to add! 💬
"""

NOT_FOUND_MESSAGE = """
❌ Sorry, I don't have a video for "{query}" yet.

**Available signs:**
{suggestions}

Try one of these or request this sign to be added!
"""
