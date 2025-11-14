# GSL Telegram Bot Setup Guide

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

### 3. Configure Bot

Edit `config.py` and replace `YOUR_BOT_TOKEN_HERE` with your actual token:

```python
BOT_TOKEN = "1234567890:ABCdefGHIjklMNOpqrsTUVwxyz"
```

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
python bot.py
```

You should see: `🤖 GSL Bot starting...`

### 6. Test Your Bot

1. Open Telegram and find your bot
2. Send `/start` to begin
3. Type any letter/word (e.g., "A" or "HELLO")
4. Receive the sign video!

---

## 📚 Bot Commands

| Command   | Description                    |
| --------- | ------------------------------ |
| `/start`  | Welcome message & instructions |
| `/help`   | Detailed usage guide           |
| `/browse` | Browse signs by category       |
| `/stats`  | View dictionary statistics     |

---

## 🎯 Usage Examples

**User:** A  
**Bot:** [Sends video showing sign for letter A]

**User:** HELLO  
**Bot:** [Sends video showing sign for "hello"]

**User:** HEL  
**Bot:** Did you mean: HELLO, HELP, HEALTH?

---

## 🔧 Troubleshooting

### Bot not responding?

- Check bot token is correct in `config.py`
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
├── bot.py              # Main bot logic
├── config.py           # Configuration & settings
├── database.py         # Video database handler
├── requirements.txt    # Python dependencies
├── README.md          # This file
└── data/
    ├── dictionary.json # Auto-generated video index
    └── videos/
        ├── alphabets/
        ├── numbers/
        └── words/
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

✅ Instant sign lookup  
✅ Fuzzy search with suggestions  
✅ Category browsing  
✅ Auto-video indexing  
✅ Statistics tracking  
✅ Error handling

---

## 🐛 Known Issues

- Large videos (>50MB) may fail to send
- First video send may be slow (Telegram caching)

---

## 📞 Support

Having issues? Check:

1. Bot token is valid
2. Videos are properly named
3. Folders exist
4. Dependencies installed

For more help, contact the developer.

---

**Happy Learning! 🤟**
