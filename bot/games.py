from __future__ import annotations

import random
import time
from typing import Any

from telegram import Update
from telegram.ext import ContextTypes

from bot.keyboards import rps_keyboard, reaction_keyboard, tic_tac_toe_keyboard
from bot import services

WORDS = ["hat", "cat", "dog", "sun", "moon", "star", "book", "code", "game", "bot", "fire", "tree", "river", "cloud", "king", "queen"]
SCRAMBLES = [("python", "Python programming language"), ("planet", "Earth is one"), ("school", "Place to study"), ("friend", "Someone close")]
EMOJI = [("🍎📱", "apple"), ("🐝🍯", "honey"), ("🌞", "sun"), ("🐶", "dog")]
SYNONYMS = {"happy": ["glad", "joyful"], "fast": ["quick", "rapid"], "smart": ["clever", "intelligent"]}
ANTONYMS = {"hot": "cold", "up": "down", "day": "night", "win": "lose"}
SPELLINGS = [("definately", "definitely"), ("recieve", "receive"), ("adress", "address")]


def reward_for(user_id: int, base: int) -> int:
    user = services.get_user(user_id) or {}
    inventory = user.get("inventory", {})
    # If user owns double coins boost, consume one charge and double reward.
    if inventory.get("double_coins", 0) > 0:
        services.use_inventory_item(user_id, "double_coins")
        return base * 2
    return base


def make_wordriddle() -> dict[str, Any]:
    chosen = random.sample(WORDS, 6)
    # Use None while placing so words do not destroy each other.
    grid: list[list[str | None]] = [[None for _ in range(8)] for _ in range(8)]
    placements = []
    placed_words: list[str] = []
    for word in chosen:
        placed = False
        for _ in range(150):
            direction = random.choice(["H", "V"])
            if direction == "H":
                r = random.randint(0, 7)
                c = random.randint(0, 8 - len(word))
                cells = [grid[r][c+i] for i in range(len(word))]
                if all(cell is None or cell == word[i] for i, cell in enumerate(cells)):
                    for i, ch in enumerate(word):
                        grid[r][c+i] = ch
                    placements.append({"word": word, "row": r, "col": c, "direction": direction})
                    placed_words.append(word)
                    placed = True
                    break
            else:
                r = random.randint(0, 8 - len(word))
                c = random.randint(0, 7)
                cells = [grid[r+i][c] for i in range(len(word))]
                if all(cell is None or cell == word[i] for i, cell in enumerate(cells)):
                    for i, ch in enumerate(word):
                        grid[r+i][c] = ch
                    placements.append({"word": word, "row": r, "col": c, "direction": direction})
                    placed_words.append(word)
                    placed = True
                    break
        if not placed:
            continue
    final_grid = [[cell if cell is not None else random.choice("abcdefghijklmnopqrstuvwxyz") for cell in row] for row in grid]
    hints = [w[0].upper() + "_" * (len(w)-1) + f" ({len(w)})" for w in placed_words]
    return {"words": placed_words, "found": [], "grid": final_grid, "hints": hints, "placements": placements}


def format_grid(grid: list[list[str]]) -> str:
    return "\n".join(" ".join(ch.upper() for ch in row) for row in grid)


def format_wordriddle(state: dict[str, Any]) -> str:
    remaining_hints = []
    for word, hint in zip(state["words"], state["hints"]):
        if word not in state.get("found", []):
            remaining_hints.append(hint)
    return (
        "🧩 WORDRIDDLE\n\n"
        f"```\n{format_grid(state['grid'])}\n```\n"
        "Hints:\n" + "\n".join(f"• {h}" for h in remaining_hints) +
        "\n\nType the word only. Example: hat"
    )


async def start_game(update: Update, context: ContextTypes.DEFAULT_TYPE, game_id: str) -> None:
    q = update.callback_query
    user_id = q.from_user.id
    chat_id = q.message.chat_id

    if game_id == "dice":
        roll = random.randint(1, 6)
        coins = reward_for(user_id, roll * 5)
        services.record_game_result(user_id, game_id, True, coins)
        await q.edit_message_text(f"🎲 You rolled {roll}! Reward: +{coins} coins.")
        return

    if game_id == "coin_flip":
        result = random.choice(["Heads", "Tails"])
        coins = reward_for(user_id, 15)
        services.record_game_result(user_id, game_id, True, coins)
        await q.edit_message_text(f"🪙 Coin result: {result}. Reward: +{coins} coins.")
        return

    if game_id == "roulette":
        unlucky = random.randint(1, 6)
        chamber = random.randint(1, 6)
        if chamber == unlucky:
            if services.use_inventory_item(user_id, "roulette_shield"):
                await q.edit_message_text("🔫 Roulette: unlucky chamber, but your shield protected you!")
                services.log("game", "roulette_shield_used", user_id=user_id)
            else:
                services.record_game_result(user_id, game_id, False, 0)
                await q.edit_message_text("🔫 Roulette: unlucky! You lost this round.")
        else:
            coins = reward_for(user_id, 60)
            services.record_game_result(user_id, game_id, True, coins)
            await q.edit_message_text(f"🔫 Roulette: survived! Reward: +{coins} coins.")
        return

    if game_id == "spin_wheel":
        rewards = [0, 10, 25, 50, 100, 150]
        coins = reward_for(user_id, random.choice(rewards))
        if coins > 0:
            services.record_game_result(user_id, game_id, True, coins)
            await q.edit_message_text(f"🎡 Wheel stopped! You won +{coins} coins.")
        else:
            services.record_game_result(user_id, game_id, False, 0)
            await q.edit_message_text("🎡 Wheel stopped on 0. Better luck next time!")
        return

    if game_id == "jackpot":
        win = random.random() < 0.18
        if win:
            coins = reward_for(user_id, 300)
            services.record_game_result(user_id, game_id, True, coins)
            await q.edit_message_text(f"💰 JACKPOT! You won +{coins} coins!")
        else:
            services.record_game_result(user_id, game_id, False, 0)
            await q.edit_message_text("💰 No jackpot this time.")
        return

    if game_id == "slot_machine":
        symbols = ["🍒", "🍋", "⭐", "💎"]
        spin = [random.choice(symbols) for _ in range(3)]
        if len(set(spin)) == 1:
            coins = reward_for(user_id, 200)
            services.record_game_result(user_id, game_id, True, coins)
            msg = f"🎰 {' '.join(spin)}\nTriple match! +{coins} coins."
        elif len(set(spin)) == 2:
            coins = reward_for(user_id, 40)
            services.record_game_result(user_id, game_id, True, coins)
            msg = f"🎰 {' '.join(spin)}\nSmall match! +{coins} coins."
        else:
            services.record_game_result(user_id, game_id, False, 0)
            msg = f"🎰 {' '.join(spin)}\nNo match."
        await q.edit_message_text(msg)
        return

    if game_id == "lucky_number":
        target = random.randint(1, 10)
        user_num = random.randint(1, 10)
        if user_num == target:
            coins = reward_for(user_id, 150)
            services.record_game_result(user_id, game_id, True, coins)
            msg = f"🔢 Your number: {user_num}\nLucky number: {target}\nPerfect! +{coins} coins."
        else:
            services.record_game_result(user_id, game_id, False, 0)
            msg = f"🔢 Your number: {user_num}\nLucky number: {target}\nNo win."
        await q.edit_message_text(msg)
        return

    if game_id == "treasure_chest":
        chests = [0, 20, 40, 100, 250]
        coins = reward_for(user_id, random.choice(chests))
        if coins:
            services.record_game_result(user_id, game_id, True, coins)
        else:
            services.record_game_result(user_id, game_id, False, 0)
        await q.edit_message_text(f"🧰 Treasure chest opened! Reward: +{coins} coins.")
        return

    if game_id == "wordriddle":
        state = make_wordriddle()
        services.start_active_game(chat_id, user_id, game_id, state)
        await q.edit_message_text(format_wordriddle(state), parse_mode="Markdown")
        return

    if game_id == "hangman":
        word = random.choice(WORDS)
        state = {"word": word, "guessed": [], "wrong": 0, "max_wrong": 6}
        services.start_active_game(chat_id, user_id, game_id, state)
        await q.edit_message_text(f"👾 Hangman started!\nWord: {' '.join('_' for _ in word)}\nType a letter or the full word.")
        return

    if game_id == "scramble":
        word, hint = random.choice(SCRAMBLES)
        scrambled = ''.join(random.sample(word, len(word)))
        services.start_active_game(chat_id, user_id, game_id, {"answer": word})
        await q.edit_message_text(f"🔤 Unscramble: `{scrambled}`\nHint: {hint}\nType the answer.", parse_mode="Markdown")
        return

    if game_id == "english_puzzle":
        data = random.choice([
            {"q": "I ___ going to school.", "answer": "am"},
            {"q": "She ___ a book yesterday.", "answer": "read"},
            {"q": "Opposite of 'small' is ___.", "answer": "big"},
        ])
        services.start_active_game(chat_id, user_id, game_id, data)
        await q.edit_message_text(f"📚 English Puzzle:\n{data['q']}\nType the missing word.")
        return

    if game_id == "emoji_guess":
        em, answer = random.choice(EMOJI)
        services.start_active_game(chat_id, user_id, game_id, {"answer": answer})
        await q.edit_message_text(f"😊 Guess the word: {em}\nType your answer.")
        return

    if game_id == "synonym":
        word = random.choice(list(SYNONYMS.keys()))
        services.start_active_game(chat_id, user_id, game_id, {"word": word, "answers": SYNONYMS[word]})
        await q.edit_message_text(f"🟰 Type a synonym of: {word}")
        return

    if game_id == "antonym":
        word, answer = random.choice(list(ANTONYMS.items()))
        services.start_active_game(chat_id, user_id, game_id, {"word": word, "answer": answer})
        await q.edit_message_text(f"↔️ Type the opposite of: {word}")
        return

    if game_id == "spelling":
        wrong, correct = random.choice(SPELLINGS)
        services.start_active_game(chat_id, user_id, game_id, {"answer": correct})
        await q.edit_message_text(f"✍️ Correct the spelling: {wrong}")
        return

    if game_id == "rps":
        await q.edit_message_text("Choose your move:", reply_markup=rps_keyboard())
        return

    if game_id == "tic_tac_toe":
        board = [" "] * 9
        services.start_active_game(chat_id, user_id, game_id, {"board": board})
        await q.edit_message_text("❌⭕ Tic Tac Toe: You are X. Tap a cell.", reply_markup=tic_tac_toe_keyboard(board))
        return

    if game_id == "number_battle":
        target = random.randint(1, 20)
        services.start_active_game(chat_id, user_id, game_id, {"target": target})
        await q.edit_message_text("🔢 Number Battle: guess a number from 1 to 20.")
        return

    if game_id == "typing_race":
        phrase = random.choice(["telegram gaming bot", "fast fingers win", "python is powerful"])
        services.start_active_game(chat_id, user_id, game_id, {"phrase": phrase, "start": time.time()})
        await q.edit_message_text(f"⌨️ Type this exactly:\n`{phrase}`", parse_mode="Markdown")
        return

    if game_id == "reaction":
        services.start_active_game(chat_id, user_id, game_id, {"start": time.time()})
        await q.edit_message_text("⚡ Reaction test ready. Tap now!", reply_markup=reaction_keyboard())
        return

    if game_id == "memory_card":
        seq = ''.join(str(random.randint(1, 9)) for _ in range(5))
        services.start_active_game(chat_id, user_id, game_id, {"answer": seq})
        await q.edit_message_text(f"🧠 Memorize this sequence and type it back:\n`{seq}`", parse_mode="Markdown")
        return

    if game_id == "math_sprint":
        a, b = random.randint(5, 30), random.randint(5, 30)
        op = random.choice(["+", "-"])
        answer = a + b if op == "+" else a - b
        services.start_active_game(chat_id, user_id, game_id, {"answer": str(answer)})
        await q.edit_message_text(f"➗ Solve: {a} {op} {b}")
        return

    if game_id == "truth_or_dare":
        prompt = random.choice(["Truth: What is your funniest mistake?", "Dare: Send one emoji that describes you.", "Truth: What game do you lose most?"])
        services.record_game_result(user_id, game_id, True, reward_for(user_id, 5))
        await q.edit_message_text(f"🔥 {prompt}")
        return

    if game_id == "whoami":
        ans = random.choice([("I am yellow and monkeys like me.", "banana"), ("I have keys but no locks.", "keyboard"), ("I shine at night.", "moon")])
        services.start_active_game(chat_id, user_id, game_id, {"answer": ans[1]})
        await q.edit_message_text(f"🤔 Who am I?\n{ans[0]}")
        return

    if game_id == "voting_battle":
        await q.edit_message_text("🗳️ Voting Battle\nVote: Which is better?\n[A] Tea\n[B] Coffee\nType A or B.")
        services.start_active_game(chat_id, user_id, game_id, {"answers": ["a", "b"]})
        return

    if game_id == "meme_caption":
        services.start_active_game(chat_id, user_id, game_id, {"open": True})
        await q.edit_message_text("😂 Meme Caption Challenge:\nSituation: When the code works on first try.\nType your caption!")
        return

    if game_id == "story_builder":
        services.start_active_game(chat_id, user_id, game_id, {"open": True})
        await q.edit_message_text("📖 Story Builder:\nContinue this sentence: 'The bot opened a secret door and...' ")
        return

    if game_id == "would_you_rather":
        await q.edit_message_text("🤷 Would you rather:\nA) Win 1,000 coins today\nB) Get 50 coins daily forever\nType A or B.")
        services.start_active_game(chat_id, user_id, game_id, {"answers": ["a", "b"]})
        return

    if game_id == "never_have_i_ever":
        services.record_game_result(user_id, game_id, True, reward_for(user_id, 5))
        await q.edit_message_text("🙈 Never have I ever sent a message to the wrong group.")
        return

    if game_id == "mafia_lite":
        role = random.choice(["Mafia", "Detective", "Citizen", "Doctor"])
        services.record_game_result(user_id, game_id, True, reward_for(user_id, 10))
        await q.edit_message_text(f"🕵️ Mafia Lite role for you: {role}\nUse this for a fun group round.")
        return

    if game_id == "matchmaking":
        await handle_matchmaking(q, user_id, game_id)
        return

    if game_id in {"duel", "tournament", "team_battle", "group_challenge"}:
        coins = reward_for(user_id, random.choice([10, 25, 50]))
        services.record_game_result(user_id, game_id, True, coins)
        await q.edit_message_text(f"{game_id.replace('_', ' ').title()} started! Basic round completed. Reward: +{coins} coins.")
        return

    await q.edit_message_text("Game not implemented yet.")


async def handle_matchmaking(q, user_id: int, game_id: str) -> None:
    db = services.get_db() if hasattr(services, "get_db") else None
    from database.mongo import get_db
    db = get_db()
    waiting = db.matchmaking_queue.find_one({"game": "quick_duel", "user_id": {"$ne": user_id}})
    if waiting:
        db.matchmaking_queue.delete_one({"_id": waiting["_id"]})
        coins = reward_for(user_id, 25)
        services.record_game_result(user_id, game_id, True, coins)
        services.record_game_result(waiting["user_id"], game_id, True, 25)
        await q.edit_message_text(f"👥 Match found! You matched with user {waiting['user_id']}. Both players get coins.")
    else:
        db.matchmaking_queue.update_one({"user_id": user_id, "game": "quick_duel"}, {"$set": {"user_id": user_id, "game": "quick_duel", "created_at": services.now_utc() if hasattr(services, "now_utc") else time.time()}}, upsert=True)
        await q.edit_message_text("👥 You joined matchmaking queue. Another player must join to match.")


def check_ttt_winner(board: list[str]) -> str | None:
    wins = [(0,1,2),(3,4,5),(6,7,8),(0,3,6),(1,4,7),(2,5,8),(0,4,8),(2,4,6)]
    for a,b,c in wins:
        if board[a] != " " and board[a] == board[b] == board[c]:
            return board[a]
    if " " not in board:
        return "draw"
    return None


async def handle_rps(update: Update, context: ContextTypes.DEFAULT_TYPE, choice: str) -> None:
    q = update.callback_query
    bot = random.choice(["rock", "paper", "scissors"])
    wins = {"rock": "scissors", "paper": "rock", "scissors": "paper"}
    if choice == bot:
        text = f"Tie! You: {choice}, Bot: {bot}."
    elif wins[choice] == bot:
        coins = reward_for(q.from_user.id, 40)
        services.record_game_result(q.from_user.id, "rps", True, coins)
        text = f"You win! You: {choice}, Bot: {bot}. +{coins} coins."
    else:
        services.record_game_result(q.from_user.id, "rps", False, 0)
        text = f"You lose! You: {choice}, Bot: {bot}."
    await q.edit_message_text("✊📄✂️ RPS\n" + text)


async def handle_reaction(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    active = services.get_active_game(q.message.chat_id, q.from_user.id)
    if not active or active["game_id"] != "reaction":
        await q.answer("No reaction game active.", show_alert=True)
        return
    elapsed = time.time() - active.get("state", {}).get("start", time.time())
    coins = max(5, int(80 - elapsed * 10))
    coins = reward_for(q.from_user.id, coins)
    services.record_game_result(q.from_user.id, "reaction", True, coins)
    services.clear_active_game(q.message.chat_id, q.from_user.id)
    await q.edit_message_text(f"⚡ Reaction time: {elapsed:.2f}s\nReward: +{coins} coins.")


async def handle_ttt(update: Update, context: ContextTypes.DEFAULT_TYPE, pos: int) -> None:
    q = update.callback_query
    active = services.get_active_game(q.message.chat_id, q.from_user.id)
    if not active or active["game_id"] != "tic_tac_toe":
        await q.answer("No Tic Tac Toe game active.", show_alert=True)
        return
    board = active["state"].get("board", [" "]*9)
    if board[pos] != " ":
        await q.answer("Cell already used.", show_alert=True)
        return
    board[pos] = "X"
    winner = check_ttt_winner(board)
    if not winner:
        empty = [i for i, v in enumerate(board) if v == " "]
        if empty:
            board[random.choice(empty)] = "O"
        winner = check_ttt_winner(board)
    if winner == "X":
        coins = reward_for(q.from_user.id, 100)
        services.record_game_result(q.from_user.id, "tic_tac_toe", True, coins)
        services.clear_active_game(q.message.chat_id, q.from_user.id)
        await q.edit_message_text(f"❌⭕ You won! +{coins} coins.", reply_markup=tic_tac_toe_keyboard(board))
    elif winner == "O":
        services.record_game_result(q.from_user.id, "tic_tac_toe", False, 0)
        services.clear_active_game(q.message.chat_id, q.from_user.id)
        await q.edit_message_text("❌⭕ Bot won this round.", reply_markup=tic_tac_toe_keyboard(board))
    elif winner == "draw":
        services.record_game_result(q.from_user.id, "tic_tac_toe", False, 10)
        services.clear_active_game(q.message.chat_id, q.from_user.id)
        await q.edit_message_text("❌⭕ Draw! +10 coins.", reply_markup=tic_tac_toe_keyboard(board))
    else:
        services.update_active_state(q.message.chat_id, q.from_user.id, {"board": board})
        await q.edit_message_text("❌⭕ Your move.", reply_markup=tic_tac_toe_keyboard(board))


async def handle_text_answer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message or not update.message.text:
        return
    user = services.ensure_user(update.effective_user)
    if user.get("banned"):
        return
    text = update.message.text.strip().lower()
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    active = services.get_active_game(chat_id, user_id)
    if not active:
        return
    game = active["game_id"]
    state = active.get("state", {})

    def finish(win: bool, coins: int, msg: str):
        if win:
            coins2 = reward_for(user_id, coins)
        else:
            coins2 = 0
        services.record_game_result(user_id, game, win, coins2)
        services.clear_active_game(chat_id, user_id)
        return msg.replace("{coins}", str(coins2))

    if game == "wordriddle":
        words = state.get("words", [])
        found = state.get("found", [])
        if text in words and text not in found:
            found.append(text)
            state["found"] = found
            if len(found) == len(words):
                coins = reward_for(user_id, 150)
                services.record_game_result(user_id, game, True, coins)
                services.clear_active_game(chat_id, user_id)
                await update.message.reply_text(f"🎉 WordRiddle complete! +{coins} coins.")
            else:
                services.update_active_state(chat_id, user_id, state)
                await update.message.reply_text(f"✅ Correct: {text}\nFound {len(found)}/{len(words)}.\n\n" + format_wordriddle(state), parse_mode="Markdown")
        else:
            await update.message.reply_text("❌ Not a hidden word or already found. Try another word.")
        return

    if game == "hangman":
        word = state["word"]
        guessed = state.get("guessed", [])
        if text == word:
            await update.message.reply_text(finish(True, 80, "🎉 Correct word! +{coins} coins."))
            return
        if len(text) == 1 and text.isalpha():
            if text not in guessed:
                guessed.append(text)
            if text not in word:
                state["wrong"] = state.get("wrong", 0) + 1
            masked = " ".join(ch if ch in guessed else "_" for ch in word)
            if all(ch in guessed for ch in word):
                await update.message.reply_text(finish(True, 80, "🎉 You completed Hangman! +{coins} coins."))
            elif state["wrong"] >= state.get("max_wrong", 6):
                await update.message.reply_text(finish(False, 0, f"💀 Hangman lost. Word was {word}."))
            else:
                services.update_active_state(chat_id, user_id, state)
                await update.message.reply_text(f"Word: {masked}\nWrong: {state['wrong']}/{state['max_wrong']}")
        return

    if game in {"scramble", "english_puzzle", "emoji_guess", "antonym", "spelling", "whoami", "math_sprint", "memory_card"}:
        answer = str(state.get("answer", "")).lower()
        if text == answer:
            await update.message.reply_text(finish(True, 60, "✅ Correct! +{coins} coins."))
        else:
            await update.message.reply_text("❌ Wrong. Try again.")
        return

    if game == "synonym":
        answers = [a.lower() for a in state.get("answers", [])]
        if text in answers:
            await update.message.reply_text(finish(True, 60, "✅ Correct synonym! +{coins} coins."))
        else:
            await update.message.reply_text("❌ Try another synonym.")
        return

    if game == "number_battle":
        try:
            guess = int(text)
        except ValueError:
            await update.message.reply_text("Type a number from 1 to 20.")
            return
        target = int(state["target"])
        diff = abs(target - guess)
        if diff == 0:
            await update.message.reply_text(finish(True, 100, f"🎯 Perfect! Target was {target}. +{{coins}} coins."))
        elif diff <= 2:
            await update.message.reply_text(finish(True, 40, f"Close! Target was {target}. +{{coins}} coins."))
        else:
            await update.message.reply_text(finish(False, 0, f"Missed. Target was {target}."))
        return

    if game == "typing_race":
        phrase = state.get("phrase", "")
        if text == phrase.lower():
            elapsed = time.time() - state.get("start", time.time())
            coins = max(20, int(120 - elapsed * 8))
            await update.message.reply_text(finish(True, coins, f"⌨️ Correct in {elapsed:.2f}s! +{{coins}} coins."))
        else:
            await update.message.reply_text("Text does not match. Try exactly again.")
        return

    if game in {"voting_battle", "would_you_rather"}:
        if text in state.get("answers", []):
            await update.message.reply_text(finish(True, 20, "Vote saved! +{coins} coins."))
        else:
            await update.message.reply_text("Type A or B.")
        return

    if game in {"meme_caption", "story_builder"}:
        await update.message.reply_text(finish(True, 25, "Nice entry! +{coins} coins."))
        return
