# 🇬🇭 Wote — GSL Learning Platform

**Competitive Ghana Sign Language (GSL) learning via Telegram + Web**

Built for the UNICEF Startup Lab — **3rd Place & Best AI Implementation** 🏆

## 🎯 Try the Bot Now!

**Live bot:** [@wotegslbot](https://t.me/wotegslbot)

Just open Telegram and search for **@wotegslbot** or [click here](https://t.me/wotegslbot) to start learning Ghana Sign Language! 🤟

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Get Your Bot Token

1. Open Telegram and search for [@BotFather](https://t.me/botfather)
2. Send `/newbot` command
3. Follow prompts to create your bot
4. Copy the **bot token** you receive

### 3. Configure Bot Using Environment Variables

**Option A: Using `.env` file (recommended for local development)**

1. Copy `.env.example` to `.env`:

   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and fill in your values:

   ```
   TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
   ADMIN_USER_ID=123456789
   LOG_LEVEL=INFO
   DB_FILE=./data/game_data.json
   ```

**Option B: Using PowerShell environment variables (temporary session)**

```powershell
$env:TELEGRAM_BOT_TOKEN="1234567890:ABCdefGHIjklMNOpqrsTUVwxyz"
$env:ADMIN_USER_ID="123456789"
$env:LOG_LEVEL="INFO"
python bot_enhanced.py
```

**Option C: Using PowerShell environment variables (persistent)**

```powershell
[Environment]::SetEnvironmentVariable("TELEGRAM_BOT_TOKEN", "1234567890:ABCdefGHIjklMNOpqrsTUVwxyz", "User")
[Environment]::SetEnvironmentVariable("ADMIN_USER_ID", "123456789", "User")
# Restart PowerShell or IDE for changes to take effect
```

**Option D: Using System Environment Variables (Windows GUI)**

1. Right-click "This PC" → Properties
2. Click "Advanced system settings"
3. Click "Environment Variables"
4. Add new User variables:
   - `TELEGRAM_BOT_TOKEN` = your token
   - `ADMIN_USER_ID` = your ID

⚠️ **IMPORTANT**: Never commit `.env` to git. It's already in `.gitignore`.

### 4. Organize Video Files

Create the following folder structure:

```
wotegslbot/
├── data/
│   └── videos/
│       ├── alphabets/    # Place A.mp4, B.mp4, etc.
│       ├── numbers/      # Place 0.mp4, 1.mp4, etc.
│       └── words/        # Place HELLO.mp4, THANK_YOU.mp4, etc.
```

**Naming Convention:**

- Alphabets: `A.mp4`, `B.mp4`, ... `Z.mp4`
- Numbers: `0.mp4`, `1.mp4`, ... `9.mp4`
- Words: `HELLO.mp4`, `THANK_YOU.mp4`, `GOODBYE.mp4`

Supported formats: `.mp4`, `.avi`, `.mov`, `.mkv`

### 5. Run the Bot

```bash
python bot_enhanced.py
```

You should see: `✅ Bot running...` in the terminal.

**Alternative (Recommended for demo):**

Run with environment variable set:

```powershell
$env:TELEGRAM_BOT_TOKEN="your-token"
python bot_enhanced.py
```

### 6. Test Your Bot

1. Open Telegram and find your bot (@wotegslbot)
2. Send `/start` to see the main menu
3. Choose:
   - **🎮 Learn with a Pal** → Solo practice or 2-player game
   - **📚 Dictionary** → Browse signs by category
4. For multiplayer: create a game room and share the code with a friend

---

## 🎮 Game Modes

### 📖 Solo Practice

- 3 quick questions to test your knowledge
- 100 points per correct answer
- Perfect for learning at your own pace

### 🎯 2-Player Multiplayer

- Create a room and share join code with a friend
- 5 synchronized questions
- Speed bonus: 50 extra points for fast answers
- Leaderboard tracking
- Real-time winner announcement

### 📚 Dictionary

- Browse all signs by category (alphabets, numbers, words)
- Video demonstrations
- Search functionality

---

## 📚 Bot Commands

| Command        | Description                             |
| -------------- | --------------------------------------- |
| `/start`       | Main menu (Practice, Dictionary, Stats) |
| `/help`        | Help & how to play                      |
| `/leaderboard` | Top 10 players                          |
| `/mystats`     | Your personal stats                     |
| `/practice`    | Start solo practice mode                |
| `/dictionary`  | Browse all signs                        |

---

## 🎯 Usage Examples

### Solo Practice Mode

```
User: /start
Bot: [Shows main menu]

User: 🎮 Learn with a Pal
Bot: Solo Practice or Create Game Room?

User: Solo Practice
Bot: Question 1/3: What is this sign?
     [Image: LAUGH]
     A) Cry  B) Laugh  C) Smile  D) Speak

User: B
Bot: ✅ Correct! +100 points
```

### 2-Player Multiplayer

```
Player 1: Create Game
Bot: Room created! Code: ROOM123

Player 2: Join room ROOM123
Bot: Player 2 joined! Waiting for start...

Player 1: Start Game
Bot: [Both players] Question 1/5: [video/image]
Player 1: LAUGH
Player 2: LAUGH
Bot: Both correct! P1: 100pts, P2: 100pts (both +50 speed bonus)
     Question 2/5: [next question]
...
Bot: Game Over! Winner: Player 1 (550 pts)
```

### Dictionary Lookup

```
User: /dictionary
Bot: Categories:
  - Alphabets (26)
  - Numbers (10)
  - Words (5+)

User: Words
Bot: [Shows: LAUGH, SPEAK, CRY, STAND, KISS]

User: LAUGH
Bot: [Sends video/image of LAUGH sign]
```

---

## 🔧 Troubleshooting

### Bot not responding?

- Check bot token is correct in `.env`
- Ensure you ran `pip install -r requirements.txt`
- Verify internet connection

### Videos not sending?

- Check video files exist in correct folders
- Verify file names match (case-sensitive: `A.mp4` not `a.mp4`)
- Ensure videos are under 50MB (Telegram limit)

### "Video file not found" error?

- Run the bot once to auto-generate `dictionary.json`
- Check paths in `dictionary.json` match actual file locations

---

## 📁 Project Structure

```
wotegslbot/
├── bot_enhanced.py           # Main bot (multiplayer + solo + dictionary)
├── game_database.py          # Game engine, leaderboard, user stats
├── database.py               # Video/media scanner
├── config.py                 # Environment config (tokens, settings)
├── requirements.txt          # Python dependencies (python-telegram-bot, python-dotenv)
├── .env.example              # Environment template
├── README.md                 # This file
├── DEMO_GUIDE.md             # Demo instructions
├── VISUAL_SHOWCASE.md        # UI mockups
└── data/
    ├── dictionary.json       # Sign definitions
    ├── game_data.json        # Leaderboard, user stats
    ├── cultural_content.json # Ghanaian context
    └── videos/
        ├── alphabets/        # A.mp4, B.mp4, ..., Z.mp4
        ├── numbers/          # 0.mp4, 1.mp4, ..., 9.mp4
        └── words/            # LAUGH.mp4, SPEAK.mp4, etc.
```

---

## 🎨 Customization

### Add New Categories

Edit `config.py`:

```python
CATEGORIES = {
    'alphabets': VIDEO_BASE_DIR / 'alphabets',
    'numbers': VIDEO_BASE_DIR / 'numbers',
    'words': VIDEO_BASE_DIR / 'words',
    'phrases': VIDEO_BASE_DIR / 'phrases',  # New category
}
```

### Change Suggestion Count

Edit `config.py`:

```python
MAX_SUGGESTIONS = 10  # Show more suggestions
```

### Add Admin Features

Set your Telegram user ID in `config.py`:

```python
ADMIN_USER_ID = 123456789  # Your Telegram ID
```

---

## 📝 Adding Videos

1. Record sign language video
2. Name it appropriately (e.g., `APPLE.mp4`)
3. Place in correct category folder
4. Restart bot (it auto-scans on startup)
5. Test: Send word to bot

The bot automatically indexes all videos in the folders!

---

## 🌟 Features

✅ **Solo Practice Mode** — 3-question quizzes with 100pts per correct answer  
✅ **2-Player Multiplayer** — Competitive synchronized games with leaderboards  
✅ **Speed Bonuses** — Earn 50 bonus points for fast answers  
✅ **Dictionary** — Browse signs by alphabets, numbers, words  
✅ **Leaderboard** — Global top 10 rankings  
✅ **User Stats** — Track wins, accuracy, total points  
✅ **Media Support** — Images (.png/.jpg) & videos (.mp4/.mov)  
✅ **Auto-Indexing** — Auto-scans media folders on startup  
✅ **Fuzzy Search** — Smart suggestions for typos  
✅ **Case-Insensitive Matching** — Exact answer validation, no partial matches

---

## 🚀 Deployment (Free Hosting)

**Recommended:** Replit (fastest, free forever)

1. Go to [replit.com](https://replit.com)
2. Create new Python repl
3. Upload bot code
4. Add `TELEGRAM_BOT_TOKEN` in Secrets
5. Run: `pip install -r requirements.txt && python bot_enhanced.py`
6. Share Replit URL with judges

**Other options:** Railway, PythonAnywhere, Heroku (paid), AWS Free Tier

## 🐛 Known Issues & Fixes

- **Bot not responding?** → Check `TELEGRAM_BOT_TOKEN` is set and correct
- **"Not enough words"?** → Ensure `data/videos/words/` has ≥4 media files
- **Videos not sending?** → Verify files are <50MB and named correctly (uppercase: LAUGH.mp4)
- **Large videos (>50MB)?** → Use ffmpeg to compress: `ffmpeg -i input.mp4 -crf 28 output.mp4`

---

## 🏆 Award

Built for the **UNICEF Startup Lab Hackathon**

- **3rd Place** overall
- **Best AI Implementation** 🥇

## 📞 Support & Contributing

Having issues?

1. Check `.env` has `TELEGRAM_BOT_TOKEN`
2. Verify media files are in correct folders
3. Run `pip install -r requirements.txt` to install all dependencies
4. Check DEMO_GUIDE.md for troubleshooting

Want to contribute? Add media files to `data/videos/` categories and open a PR!

---

**Built with ❤️ for the Ghanaian Deaf Community**  
**Let's learn Ghana Sign Language together! 🤟**
