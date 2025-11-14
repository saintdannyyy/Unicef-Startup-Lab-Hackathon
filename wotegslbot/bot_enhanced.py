"""
Ghanaian Sign Language (GSL) Telegram Bot
Dictionary + Competitive Multiplayer Games with Ghanaian Cultural Integration
"""
import logging
from pathlib import Path
from typing import Dict, List, Optional
import random
import time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    ConversationHandler,
    filters
)

from config import BOT_TOKEN, ADMIN_USER_ID, MAX_SUGGESTIONS
from database import db
from game_database import game_db

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Conversation states
WAITING_FOR_OPPONENT, ANSWER_QUESTION = range(2)


# ========================
# MAIN MENU HANDLERS
# ========================

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Welcome message with main menu"""
    user = update.effective_user
    
    # Register user in game database
    game_db.get_or_create_user(user.id, user.username, user.first_name)
    
    keyboard = [
        [
            InlineKeyboardButton("🎮 Learn with a Pal", callback_data='menu_multiplayer'),
            InlineKeyboardButton("📚 Dictionary", callback_data='menu_dictionary')
        ],
        [
            InlineKeyboardButton("🏆 Leaderboard", callback_data='menu_leaderboard'),
            InlineKeyboardButton("📊 My Stats", callback_data='menu_stats')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_text = f"""
🇬🇭 **Akwaaba, {user.first_name}!** 🤟

Welcome to the **Ghana Sign Language Learning Bot**!

**🎮 Learn with a Pal**
Play 2-player activity recognition games with friends!

**📚 Dictionary**
Search for GSL signs and watch video demonstrations

**🏆 Leaderboard**
See top players and your ranking

Choose an option below to begin your GSL journey! 🌟
    """
    
    await update.message.reply_text(
        welcome_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )


async def menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle main menu selections"""
    query = update.callback_query
    await query.answer()
    
    if query.data == 'menu_multiplayer':
        await show_multiplayer_menu(query, context)
    elif query.data == 'menu_dictionary':
        await show_dictionary_menu(query, context)
    elif query.data == 'menu_leaderboard':
        await show_leaderboard(query, context)
    elif query.data == 'menu_stats':
        await show_user_stats(query, context)
    elif query.data == 'back_to_main':
        await back_to_main_menu(query, context)



async def back_to_main_menu(query, context: ContextTypes.DEFAULT_TYPE):
    """Return to main menu"""
    user = query.from_user
    
    keyboard = [
        [
            InlineKeyboardButton("🎮 Learn with a Pal", callback_data='menu_multiplayer'),
            InlineKeyboardButton("📚 Dictionary", callback_data='menu_dictionary')
        ],
        [
            InlineKeyboardButton("🏆 Leaderboard", callback_data='menu_leaderboard'),
            InlineKeyboardButton("📊 My Stats", callback_data='menu_stats')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    text = f"""
🇬🇭 **Akwaaba, {user.first_name}!** 🤟

Choose an option to continue:
    """
    
    await query.edit_message_text(
        text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )


# ========================
# MULTIPLAYER GAME HANDLERS
# ========================

async def show_multiplayer_menu(query, context: ContextTypes.DEFAULT_TYPE):
    """Show multiplayer game modes"""
    keyboard = [
        [InlineKeyboardButton("👤 Practice Solo", callback_data='game_solo')],
        [InlineKeyboardButton("🎯 Create New Game", callback_data='game_create')],
        [InlineKeyboardButton("🔗 Join Game", callback_data='game_join')],
        [InlineKeyboardButton("🔙 Back to Menu", callback_data='back_to_main')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    text = """
🎮 **Learn with a Pal**

**👤 Practice Solo**
Practice alone with 3 quick questions!

**🎯 Create New Game**
Start a new activity recognition game and invite a friend!

**🔗 Join Game**
Enter a room code to join your friend's game

🎲 Learn GSL and have fun! 🏆
    """
    
    await query.edit_message_text(
        text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )


async def game_mode_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle game mode selection"""
    query = update.callback_query
    await query.answer()
    
    if query.data == 'game_solo':
        await start_solo_practice(query, context)
    elif query.data == 'game_create':
        await create_game_room(query, context, 'activities')
    elif query.data == 'game_join':
        await prompt_join_code(query, context)


# ========================
# SOLO PRACTICE HANDLERS
# ========================

async def start_solo_practice(query, context: ContextTypes.DEFAULT_TYPE):
    """Start solo practice session"""
    user_id = query.from_user.id
    
    room_id = game_db.create_solo_practice(user_id)
    
    if not room_id:
        await query.edit_message_text(
            "⚠️ Not enough words available for practice. Please add more words to the dictionary!",
            parse_mode='Markdown'
        )
        return
    
    # Send first question
    await send_solo_question(query.message.chat_id, room_id, context)


async def send_solo_question(chat_id: int, room_id: str, context: ContextTypes.DEFAULT_TYPE):
    """Send a solo practice question"""
    game_state = game_db.get_game_state(room_id)
    if not game_state:
        return
    
    question = game_db.get_current_question(room_id)
    if not question:
        return
    
    # Send video/image if available
    video_sign = question.get('video_sign')
    if video_sign:
        result = db.search(video_sign)
        if result:
            media_path = Path(result['path'])
            if media_path.exists():
                try:
                    with open(media_path, 'rb') as media_file:
                        # Check if it's an image or video
                        if result.get('type') == 'image':
                            await context.bot.send_photo(
                                chat_id=chat_id,
                                photo=media_file,
                                caption=f"🖼️ Question {game_state['current_question'] + 1}/3"
                            )
                        else:
                            await context.bot.send_video(
                                chat_id=chat_id,
                                video=media_file,
                                caption=f"🎥 Question {game_state['current_question'] + 1}/3"
                            )
                except Exception as e:
                    logger.error(f"Error sending media: {e}")
    
    # Create answer buttons
    keyboard = []
    for option in question['options']:
        keyboard.append([
            InlineKeyboardButton(
                option.title(),
                callback_data=f'solopractice_{room_id}_{option}'
            )
        ])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    question_text = f"""
📝 **{question['question']}**

Choose the correct sign:
    """
    
    await context.bot.send_message(
        chat_id=chat_id,
        text=question_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )


async def solo_answer_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle solo practice answer"""
    query = update.callback_query
    await query.answer()
    
    try:
        # Parse callback data: solopractice_roomid_answer
        # Room ID format: solo_userid_timestamp
        parts = query.data.split('_', 1)  # Split into ['solopractice', 'roomid_answer']
        if len(parts) < 2:
            await query.edit_message_text("⚠️ Invalid answer format.")
            return
        
        # Now split the rest to separate room_id from answer
        # Format: solo_userid_timestamp_ANSWER
        remaining = parts[1]
        # Find the last underscore to separate answer from room_id
        last_underscore = remaining.rfind('_')
        if last_underscore == -1:
            await query.edit_message_text("⚠️ Invalid answer format.")
            return
        
        room_id = remaining[:last_underscore]
        answer = remaining[last_underscore + 1:]
        user_id = query.from_user.id
        
        # Submit answer
        result = game_db.submit_solo_answer(room_id, user_id, answer)
        
        if not result['success']:
            logger.error(f"Solo answer submission failed: {result.get('error', 'Unknown error')}")
            await query.edit_message_text(f"⚠️ Error submitting answer: {result.get('error', 'Unknown error')}")
            return
        
        # Show feedback
        if result['correct']:
            feedback = f"✅ **Correct!** +{result['points_earned']} points\n\n"
        else:
            feedback = f"❌ **Incorrect!**\nCorrect answer: **{result['correct_answer'].title()}**\n\n"
        
        feedback += f"💯 Score: {result['current_score']}"
        
        await query.edit_message_text(feedback, parse_mode='Markdown')
        
        # Check if game finished
        if result['is_finished']:
            final_text = f"""
🎉 **Practice Complete!**

📊 **Final Score:** {result['current_score']}/{result['total_questions'] * 100}
✅ **Questions:** {result['question_number']}/{result['total_questions']}

Great job practicing GSL! 🌟

Want to practice again or play with a friend?
        """
            
            keyboard = [
                [InlineKeyboardButton("🔄 Practice Again", callback_data='game_solo')],
                [InlineKeyboardButton("👥 Play with Friend", callback_data='menu_multiplayer')],
                [InlineKeyboardButton("🏠 Main Menu", callback_data='back_to_main')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await context.bot.send_message(
                chat_id=query.message.chat_id,
                text=final_text,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
        else:
            # Send next question after a brief delay
            await asyncio.sleep(1.5)
            await send_solo_question(query.message.chat_id, room_id, context)
    
    except Exception as e:
        logger.error(f"Error in solo_answer_callback: {e}", exc_info=True)
        await query.edit_message_text("⚠️ Error submitting answer. Please try again or start a new practice session.")


async def prompt_join_code(query, context: ContextTypes.DEFAULT_TYPE):
    """Prompt user to enter join code"""
    keyboard = [[InlineKeyboardButton("🔙 Back", callback_data='menu_multiplayer')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    text = """
🔗 **Join a Game**

Enter the 4-digit room code your friend shared:

Type the code (e.g., 1234)
    """
    
    # Set conversation state
    context.user_data['waiting_for_join_code'] = True
    
    await query.edit_message_text(
        text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )


async def create_game_room(query, context: ContextTypes.DEFAULT_TYPE, game_mode: str):
    """Create a game room and wait for opponent"""
    user = query.from_user
    
    # Create game room
    room_id = game_db.create_game_room(user.id, game_mode)
    game_state = game_db.get_game_state(room_id)
    room_code = game_state['room_code']
    
    # Store player name
    game_state['player_names'][str(user.id)] = user.first_name or user.username or "Player 1"
    
    context.user_data['current_room'] = room_id
    context.user_data['is_host'] = True
    
    keyboard = [
        [InlineKeyboardButton("✅ Start Game (2 Players Ready)", callback_data=f'start_game_{room_id}')],
        [InlineKeyboardButton("❌ Cancel", callback_data='menu_multiplayer')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    text = f"""
🎮 **Game Room Created!**

**Room Code:** `{room_code}`

**Share this code with your friend!**
They can join by:
1. Click "Learn with a Pal"
2. Click "Join Game"
3. Enter code: {room_code}

**Players:** 1/2
• {user.first_name or 'You'}

⏳ Waiting for player 2...

_The "Start Game" button will activate when both players are ready!_
    """
    
    await query.edit_message_text(
        text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )


async def start_game_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start the game"""
    query = update.callback_query
    await query.answer()
    
    # Extract room_id from callback data
    room_id = query.data.replace('start_game_', '')
    
    game_state = game_db.get_game_state(room_id)
    
    # Check if 2 players
    if len(game_state['players']) < 2:
        await query.answer("⏳ Waiting for player 2...", show_alert=True)
        return
    
    # Start game
    success = game_db.start_game(room_id)
    
    if not success:
        await query.edit_message_text("⚠️ Failed to start game. Please try again.")
        return
    
    # Notify both players
    for player_id in game_state['players']:
        try:
            await context.bot.send_message(
                chat_id=player_id,
                text="🎮 **Game Starting!**\n\nGet ready for the first question...",
                parse_mode='Markdown'
            )
        except:
            pass
    
    # Send first question to both players
    await send_question_to_all_players(context, room_id, 0)


async def send_question_to_all_players(context: ContextTypes.DEFAULT_TYPE, room_id: str, question_idx: int):
    """Send question to all players in the room"""
    game_state = game_db.get_game_state(room_id)
    
    if not game_state:
        logger.error(f"send_question_to_all_players: Game state not found for room {room_id}")
        await end_game_for_all_players(context, room_id)
        return
    
    num_questions = len(game_state.get('questions', []))
    logger.info(f"send_question_to_all_players: room={room_id}, question_idx={question_idx}, total_questions={num_questions}")
    
    if question_idx >= num_questions:
        logger.info(f"send_question_to_all_players: No more questions, ending game")
        # End game for all players
        await end_game_for_all_players(context, room_id)
        return
    
    # Set question start time
    game_state['question_start_time'] = time.time()
    
    question = game_state['questions'][question_idx]
    
    # Create keyboard with multiple choice options
    keyboard = []
    for option in question.get('options', []):
        keyboard.append([InlineKeyboardButton(option.title(), callback_data=f'answer_{room_id}_{option}')])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    question_text = f"""
❓ **Question {question_idx + 1}/{len(game_state['questions'])}**

{question['question']}

**Select the correct sign:**
    """
    
    # Send to all players
    for player_id in game_state['players']:
        try:
            # Send video/image if available
            video_sign = question.get('video_sign')
            if video_sign:
                result = db.search(video_sign)
                if result:
                    media_path = Path(result['path'])
                    if media_path.exists():
                        with open(media_path, 'rb') as media_file:
                            if result.get('type') == 'image':
                                await context.bot.send_photo(
                                    chat_id=player_id,
                                    photo=media_file,
                                    caption="🖼️ Look carefully!"
                                )
                            else:
                                await context.bot.send_video(
                                    chat_id=player_id,
                                    video=media_file,
                                    caption="🎥 Watch carefully!"
                                )
            
            # Send question
            await context.bot.send_message(
                chat_id=player_id,
                text=question_text,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
        except Exception as e:
            logger.error(f"Error sending question to player {player_id}: {e}")


async def answer_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle answer button click"""
    query = update.callback_query
    
    try:
        # Parse callback data
        parts = query.data.split('_', 2)
        if len(parts) < 3:
            await query.answer("Invalid answer format", show_alert=True)
            return
        
        room_id = parts[1]
        answer = parts[2]
        
        game_state = game_db.get_game_state(room_id)
        if not game_state:
            await query.answer("Game has ended", show_alert=True)
            await query.edit_message_text("⚠️ Game has ended. Thanks for playing!")
            return
        
        # Check if game is already finished
        if game_state.get('status') == 'finished':
            await query.answer("Game has ended", show_alert=True)
            await query.edit_message_text("⚠️ Game has ended. Thanks for playing!")
            return
        
        user_id = query.from_user.id
        
        # Check if already answered
        if user_id in game_state.get('players_answered', set()):
            await query.answer("You already answered this question!", show_alert=True)
            return
        
        # Answer the callback query first
        await query.answer()
        
        # Record answer
        game_state['players_answered'].add(user_id)
        game_state.setdefault('question_start_time', time.time())
        time_taken = time.time() - game_state['question_start_time']
        
        result = game_db.submit_answer(room_id, user_id, answer, time_taken)
        
        # Show feedback
        feedback_emoji = "✅" if result['is_correct'] else "❌"
        await query.edit_message_text(
            f"{feedback_emoji} **{'Correct!' if result['is_correct'] else 'Incorrect'}**\n\n"
            f"Your answer: {answer}\n"
            f"Correct answer: {result['correct_answer']}\n\n"
            f"Points: +{result['points']} 🌟\n"
            f"Total: {result['total_score']} ⭐\n\n"
            f"⏳ Waiting for other player...",
            parse_mode='Markdown'
        )
        
        # Check if both players answered
        if len(game_state['players_answered']) >= len(game_state['players']):
            # Clear answered set for next question
            game_state['players_answered'].clear()
            
            # Reset question start time
            game_state['question_start_time'] = time.time()
            
            # Move to next question after delay
            import asyncio
            await asyncio.sleep(2)
            
            # Check if there are more questions
            if game_state['current_question'] + 1 < len(game_state['questions']):
                # Move to next question
                game_state['current_question'] += 1
                await send_question_to_all_players(context, room_id, game_state['current_question'])
            else:
                # Game over - mark as finished first to prevent double-processing
                game_state['status'] = 'finished'
                await end_game_for_all_players(context, room_id)
    
    except Exception as e:
        logger.error(f"Error in answer_callback: {e}", exc_info=True)
        try:
            await query.answer("Error processing answer", show_alert=True)
        except:
            pass


async def end_game_for_all_players(context: ContextTypes.DEFAULT_TYPE, room_id: str):
    """End game and show results to all players"""
    game_state = game_db.get_game_state(room_id)
    
    if not game_state:
        return
    
    # Finalize game (this will also remove it from active_games)
    results = game_db._finalize_game(room_id)
    
    # Get winner info
    winner_user = game_db.get_or_create_user(results['winner_id'])
    
    results_text = f"""
🏆 **Game Over!**

**Winner:** {winner_user.get('first_name', 'Player')} 🎉

**Final Scores:**
"""
    
    for i, (player_id, score) in enumerate(results['final_scores'], 1):
        player = game_db.get_or_create_user(int(player_id))
        medal = "🥇" if i == 1 else "🥈"
        results_text += f"\n{medal} {player.get('first_name', 'Player')}: {score} points"
    
    results_text += f"""

**Total Questions:** {results['stats']['total_questions']}

🎊 Medaase! Keep learning GSL! 🤟
    """
    
    # Send to all players
    for player_id in game_state['players']:
        try:
            keyboard = [[InlineKeyboardButton("🏠 Main Menu", callback_data='back_to_main')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await context.bot.send_message(
                chat_id=player_id,
                text=results_text,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
        except Exception as e:
            logger.error(f"Error sending results to player {player_id}: {e}")


async def send_question(query, context: ContextTypes.DEFAULT_TYPE, room_id: str, question_idx: int):
    """Send a quiz question"""
    game_state = game_db.get_game_state(room_id)
    
    if not game_state or question_idx >= len(game_state['questions']):
        await end_game(query, context, room_id)
        return
    
    question = game_state['questions'][question_idx]
    
    # Store question start time
    context.user_data['question_start_time'] = time.time()
    context.user_data['current_room'] = room_id
    context.user_data['current_question'] = question_idx
    
    keyboard = []
    
    # For now, show text input prompt (in production, could show multiple choice)
    keyboard.append([InlineKeyboardButton("⏭️ Skip", callback_data=f'skip_{room_id}_{question_idx}')])
    keyboard.append([InlineKeyboardButton("❌ Quit Game", callback_data='quit_game')])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    question_text = f"""
❓ **Question {question_idx + 1}/{len(game_state['questions'])}**

{question['question']}

**Signs to learn:** {', '.join(question.get('signs_to_show', []))}

{question.get('symbol', '')} {question.get('lesson', '')}

💬 Type your answer below:
    """
    
    await query.edit_message_text(
        question_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )


async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle user's answer to question or join code"""
    # Check if waiting for join code
    if context.user_data.get('waiting_for_join_code'):
        room_code = update.message.text.strip()
        
        # Find room by code
        room_id = game_db.find_room_by_code(room_code)
        
        if not room_id:
            await update.message.reply_text(
                f"❌ Room code `{room_code}` not found.\n\n"
                f"Please check the code and try again, or ask your friend for a new code.",
                parse_mode='Markdown'
            )
            return
        
        # Try to join
        user = update.effective_user
        success = game_db.join_game_room(room_id, user.id, user.first_name or user.username)
        
        if success:
            context.user_data['current_room'] = room_id
            context.user_data['is_host'] = False
            context.user_data.pop('waiting_for_join_code', None)
            
            game_state = game_db.get_game_state(room_id)
            host_name = game_state['player_names'].get(str(game_state['host_id']), 'Player 1')
            
            await update.message.reply_text(
                f"✅ **Joined successfully!**\n\n"
                f"**Room Code:** `{room_code}`\n"
                f"**Players:** 2/2\n"
                f"• {host_name}\n"
                f"• {user.first_name or 'You'}\n\n"
                f"🎮 Waiting for host to start the game...",
                parse_mode='Markdown'
            )
            
            # Notify host
            try:
                await context.bot.send_message(
                    chat_id=game_state['host_id'],
                    text=f"🎉 **Player 2 joined!**\n\n{user.first_name or 'A player'} is ready to play!\n\nYou can now start the game!",
                    parse_mode='Markdown'
                )
            except:
                pass
        else:
            await update.message.reply_text(
                f"❌ Cannot join room `{room_code}`.\n\n"
                f"Room might be full or game already started.",
                parse_mode='Markdown'
            )
        return
    
    # Check if user is in an active game
    if 'current_room' not in context.user_data:
        # Not in a game, treat as dictionary search
        await handle_dictionary_search(update, context)
        return
    
    room_id = context.user_data['current_room']
    question_idx = context.user_data.get('current_question', 0)
    
    game_state = game_db.get_game_state(room_id)
    
    if not game_state or game_state['status'] != 'playing':
        # Game ended or not found
        await handle_dictionary_search(update, context)
        return
    
    answer = update.message.text.strip()
    time_taken = time.time() - context.user_data.get('question_start_time', time.time())
    
    # Submit answer
    result = game_db.submit_answer(room_id, update.effective_user.id, answer, time_taken)
    
    if result['success']:
        feedback_emoji = "✅" if result['is_correct'] else "❌"
        feedback_text = f"""
{feedback_emoji} **{'Correct!' if result['is_correct'] else 'Incorrect'}**

Your answer: {answer}
Correct answer: {result['correct_answer']}

**Points earned:** {result['points']} 🌟
**Total score:** {result['total_score']} ⭐

{'🔥 Great job!' if result['is_correct'] else '💪 Keep trying!'}
        """
        
        await update.message.reply_text(feedback_text, parse_mode='Markdown')
        
        # Wait a moment, then send next question
        await asyncio.sleep(2)
        
        next_q = game_db.next_question(room_id)
        
        if next_q:
            # More questions remain
            keyboard = [[InlineKeyboardButton("➡️ Next Question", callback_data=f'next_{room_id}')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(
                "Ready for the next question?",
                reply_markup=reply_markup
            )
        else:
            # Game over
            await end_game_message(update, context, room_id)


async def end_game(query, context: ContextTypes.DEFAULT_TYPE, room_id: str):
    """End game and show results"""
    game_state = game_db.get_game_state(room_id)
    
    if not game_state:
        await query.edit_message_text("⚠️ Game not found.")
        return
    
    # Finalize game
    results = game_db._finalize_game(room_id)
    
    # Get winner info
    winner_user = game_db.get_or_create_user(results['winner_id'])
    
    keyboard = [[InlineKeyboardButton("🏠 Main Menu", callback_data='back_to_main')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    results_text = f"""
🏆 **Game Over!**

**Winner:** {winner_user.get('first_name', 'Player')} 🎉
**Score:** {results['winner_score']} points ⭐

**Final Scores:**
"""
    
    for i, (player_id, score) in enumerate(results['final_scores'], 1):
        player = game_db.get_or_create_user(int(player_id))
        medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉"
        results_text += f"\n{medal} {player.get('first_name', 'Player')}: {score} points"
    
    results_text += f"""

**Total Questions:** {results['stats']['total_questions']}
**Game Mode:** {results['stats']['game_mode'].replace('_', ' ').title()}

🎊 Congratulations! Keep learning GSL! 🤟
    """
    
    # Clear game from user data
    context.user_data.pop('current_room', None)
    context.user_data.pop('current_question', None)
    
    await query.edit_message_text(
        results_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )


async def end_game_message(update: Update, context: ContextTypes.DEFAULT_TYPE, room_id: str):
    """End game with message (not callback query)"""
    game_state = game_db.get_game_state(room_id)
    
    if not game_state:
        await update.message.reply_text("⚠️ Game not found.")
        return
    
    results = game_db._finalize_game(room_id)
    winner_user = game_db.get_or_create_user(results['winner_id'])
    
    keyboard = [[InlineKeyboardButton("🏠 Main Menu", callback_data='back_to_main')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    results_text = f"""
🏆 **Game Over!**

**Winner:** {winner_user.get('first_name', 'Player')} 🎉
**Score:** {results['winner_score']} points ⭐

**Final Scores:**
"""
    
    for i, (player_id, score) in enumerate(results['final_scores'], 1):
        player = game_db.get_or_create_user(int(player_id))
        medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉"
        results_text += f"\n{medal} {player.get('first_name', 'Player')}: {score} points"
    
    results_text += f"""

**Total Questions:** {results['stats']['total_questions']}

🎊 Medaase! Keep learning GSL! 🤟
    """
    
    context.user_data.pop('current_room', None)
    context.user_data.pop('current_question', None)
    
    await update.message.reply_text(
        results_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )


# ========================
# DICTIONARY HANDLERS
# ========================

async def show_dictionary_menu(query, context: ContextTypes.DEFAULT_TYPE):
    """Show dictionary browsing options"""
    keyboard = [
        [
            InlineKeyboardButton("🔤 Alphabets", callback_data='browse_alphabets'),
            InlineKeyboardButton("🔢 Numbers", callback_data='browse_numbers')
        ],
        [InlineKeyboardButton("💬 Words", callback_data='browse_words')],
        [InlineKeyboardButton("📊 Dictionary Stats", callback_data='dict_stats')],
        [InlineKeyboardButton("🔙 Back to Menu", callback_data='back_to_main')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    text = """
📚 **GSL Dictionary**

Browse sign language videos by category or search directly:

**🔤 Alphabets** - A to Z fingerspelling
**🔢 Numbers** - Number signs
**💬 Words** - Common words and phrases

💡 **Quick Search:** Just type any word to see its sign!
    """
    
    await query.edit_message_text(
        text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )


async def browse_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle category browsing callbacks"""
    query = update.callback_query
    await query.answer()
    
    category = query.data.replace('browse_', '')
    items = db.get_category(category)
    
    if not items:
        keyboard = [[InlineKeyboardButton("🔙 Back", callback_data='menu_dictionary')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            f"📭 No signs available in **{category}** yet.",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        return
    
    # Create list of available signs
    signs_list = ', '.join(sorted(items.keys())[:50])
    total = len(items)
    
    keyboard = [[InlineKeyboardButton("🔙 Back to Dictionary", callback_data='menu_dictionary')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    message = f"""
📖 **{category.capitalize()}** ({total} signs)

Available: {signs_list}

Type any of these to see the sign video!
    """
    
    if total > 50:
        message += f"\n\n_...and {total - 50} more!_"
    
    await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')


async def dict_stats_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show dictionary statistics"""
    query = update.callback_query
    await query.answer()
    
    stats = db.get_statistics()
    
    keyboard = [[InlineKeyboardButton("🔙 Back", callback_data='menu_dictionary')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    stats_text = f"""
📊 **GSL Dictionary Statistics**

**Total Signs:** {stats['total_signs']} 🤟

🔤 Alphabets: {stats['alphabets']}
🔢 Numbers: {stats['numbers']}
💬 Words: {stats['words']}

Keep learning! 🌟
    """
    
    await query.edit_message_text(stats_text, reply_markup=reply_markup, parse_mode='Markdown')


async def handle_dictionary_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle user queries for signs"""
    query = update.message.text.strip()
    
    # Search for exact match
    result = db.search(query)
    
    if result:
        # Found exact match
        await send_sign_video(update, result)
    else:
        # Try fuzzy search
        suggestions = db.fuzzy_search(query, max_results=MAX_SUGGESTIONS)
        
        if suggestions:
            await send_suggestions(update, query, suggestions)
        else:
            await update.message.reply_text(
                f"❌ Sorry, I couldn't find any sign for **'{query}'**.\n\n"
                f"📚 **Help us build an inclusive GSL dictionary!**\n"
                f"This is a community-driven project - for the inclusive, by the inclusive.\n\n"
                f"🎥 **Contribute your signs:**\n"
                f"Visit our data collection app to record and submit GSL signs:\n"
                f"https://unchancy-deadpan-codi.ngrok-free.dev\n\n"
                f"💡 Try /browse to see available signs or play a game to learn more!",
                parse_mode='Markdown'
            )


async def send_sign_video(update: Update, video_info: Dict):
    """Send video or image file for a sign"""
    media_path = Path(video_info['path'])
    
    if not media_path.exists():
        await update.message.reply_text(
            "⚠️ Media file not found. Please contact admin.",
            parse_mode='Markdown'
        )
        return
    
    caption = f"""
✅ **{video_info.get('description', 'GSL Sign')}**
Category: {video_info.get('category', 'Unknown').capitalize()}
    """
    
    try:
        with open(media_path, 'rb') as media_file:
            if video_info.get('type') == 'image':
                await update.message.reply_photo(
                    photo=media_file,
                    caption=caption,
                    parse_mode='Markdown'
                )
            else:
                await update.message.reply_video(
                    video=media_file,
                    caption=caption,
                    parse_mode='Markdown'
                )
    except Exception as e:
        logger.error(f"Error sending media: {e}")
        await update.message.reply_text(
            "⚠️ Error sending media. Please try again later.",
            parse_mode='Markdown'
        )


async def send_suggestions(update: Update, query: str, suggestions: List[Dict]):
    """Send suggestions when exact match not found"""
    suggestions_text = f"🔍 Didn't find **'{query}'**, but here are similar signs:\n\n"
    
    for i, item in enumerate(suggestions, 1):
        suggestions_text += f"{i}. {item['word']} ({item['category']})\n"
    
    suggestions_text += "\n💡 Type any of these to see the sign!"
    
    await update.message.reply_text(suggestions_text, parse_mode='Markdown')


# ========================
# LEADERBOARD & STATS
# ========================

async def show_leaderboard(query, context: ContextTypes.DEFAULT_TYPE):
    """Display global leaderboard"""
    leaderboard = game_db.get_leaderboard(10)
    
    keyboard = [[InlineKeyboardButton("🔙 Back to Menu", callback_data='back_to_main')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    text = "🏆 **Global Leaderboard - Top 10**\n\n"
    
    for i, player in enumerate(leaderboard, 1):
        medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
        name = player.get('first_name', player.get('username', 'Anonymous'))
        text += f"{medal} **{name}** - {player['total_points']} pts ({player['wins']}W)\n"
    
    if not leaderboard:
        text += "No players yet. Be the first to play! 🎮"
    
    text += "\n💪 Play games to climb the leaderboard!"
    
    await query.edit_message_text(
        text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )


async def show_user_stats(query, context: ContextTypes.DEFAULT_TYPE):
    """Show user's personal statistics"""
    user = query.from_user
    rank, player_stats = game_db.get_user_rank(user.id)
    
    keyboard = [[InlineKeyboardButton("🔙 Back to Menu", callback_data='back_to_main')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    rank_text = f"#{rank}" if rank else "Unranked"
    win_rate = (player_stats['wins'] / player_stats['total_games'] * 100) if player_stats['total_games'] > 0 else 0
    
    text = f"""
📊 **Your GSL Stats**

**Rank:** {rank_text} 🏅
**Total Points:** {player_stats['total_points']} ⭐
**Games Played:** {player_stats['total_games']} 🎮
**Wins:** {player_stats['wins']} 🏆
**Win Rate:** {win_rate:.1f}% 📈
**Current Streak:** {player_stats['streak']} 🔥

**Achievements:** {len(player_stats['achievements'])} 🎖️

Keep playing to improve your stats! 💪
    """
    
    await query.edit_message_text(
        text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )


# ========================
# CULTURAL LESSONS
# ========================

async def show_cultural_menu(query, context: ContextTypes.DEFAULT_TYPE):
    """Show Ghanaian cultural learning menu"""
    keyboard = [
        [InlineKeyboardButton("📜 Proverbs", callback_data='cultural_proverbs_learn')],
        [InlineKeyboardButton("🎨 Adinkra Symbols", callback_data='cultural_symbols_learn')],
        [InlineKeyboardButton("👋 Greetings", callback_data='cultural_greetings_learn')],
        [InlineKeyboardButton("🍲 Food Culture", callback_data='cultural_food_learn')],
        [InlineKeyboardButton("🔙 Back to Menu", callback_data='back_to_main')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    text = """
🇬🇭 **Ghanaian Cultural Lessons**

Learn about Ghana's rich culture through sign language!

**📜 Proverbs** - Akan wisdom and sayings
**🎨 Adinkra Symbols** - Traditional symbols and meanings
**👋 Greetings** - Ghanaian greetings in GSL
**🍲 Food Culture** - Traditional Ghanaian dishes

Combine cultural knowledge with GSL learning! 🌟
    """
    
    await query.edit_message_text(
        text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )


async def cultural_content_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show cultural content"""
    query = update.callback_query
    await query.answer()
    
    if query.data == 'cultural_proverbs_learn':
        proverb = game_db.get_random_proverb()
        
        keyboard = [
            [InlineKeyboardButton("🎮 Quiz Me!", callback_data='game_proverbs')],
            [InlineKeyboardButton("📜 Another Proverb", callback_data='cultural_proverbs_learn')],
            [InlineKeyboardButton("🔙 Back", callback_data='menu_cultural')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        text = f"""
📜 **Ghanaian Proverb**

**Akan:** {proverb['akan']}

**English:** {proverb['english']}

**Lesson:** {proverb['lesson']}

**GSL Signs to learn:** {', '.join(proverb['signs'])}

💡 Type any of these signs to see the video!
        """
        
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')


# ========================
# UTILITY COMMANDS
# ========================

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show help message"""
    help_text = """
🤟 **GSL Bot Help**

**Main Features:**
🎮 Play multiplayer games
📚 Search sign videos
🏆 Compete on leaderboard
🇬🇭 Learn Ghanaian culture

**Quick Tips:**
• Use /start to see the main menu
• Type any word to search GSL signs
• Challenge friends in quiz games
• Earn points and achievements!

Need more help? Just explore the menus! 😊
    """
    
    await update.message.reply_text(help_text, parse_mode='Markdown')


# ========================
# ERROR HANDLER
# ========================

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Log errors"""
    logger.error(f"Update {update} caused error {context.error}")


# ========================
# MAIN FUNCTION
# ========================

import asyncio

def main():
    """Start the bot"""
    # Create application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    
    # Main menu callbacks
    application.add_handler(CallbackQueryHandler(menu_callback, pattern='^menu_'))
    
    # Game callbacks
    application.add_handler(CallbackQueryHandler(game_mode_callback, pattern='^game_'))
    application.add_handler(CallbackQueryHandler(start_game_callback, pattern='^start_game_'))
    application.add_handler(CallbackQueryHandler(answer_callback, pattern='^answer_'))
    application.add_handler(CallbackQueryHandler(solo_answer_callback, pattern='^solopractice_'))
    
    # Dictionary callbacks
    application.add_handler(CallbackQueryHandler(browse_callback, pattern='^browse_'))
    application.add_handler(CallbackQueryHandler(dict_stats_callback, pattern='^dict_stats'))
    
    # Message handler (for answers and dictionary searches)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_answer))
    
    # Error handler
    application.add_error_handler(error_handler)
    
    # Start bot
    logger.info("🤖 GSL Bot with 2-Player Activity Recognition starting...")
    logger.info("🇬🇭 Learn GSL together!")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
