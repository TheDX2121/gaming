GAME_CATEGORIES = {
    "luck": {
        "title": "🎲 Luck Games",
        "games": [
            "dice", "coin_flip", "roulette", "spin_wheel", "jackpot", "slot_machine", "lucky_number", "treasure_chest"
        ],
    },
    "word": {
        "title": "🧠 Word Games",
        "games": [
            "wordriddle", "hangman", "scramble", "english_puzzle", "emoji_guess", "synonym", "antonym", "spelling"
        ],
    },
    "competitive": {
        "title": "⚔️ Competitive Games",
        "games": [
            "rps", "tic_tac_toe", "number_battle", "typing_race", "reaction", "memory_card", "math_sprint"
        ],
    },
    "fun": {
        "title": "🎭 Fun Group Games",
        "games": [
            "truth_or_dare", "whoami", "voting_battle", "meme_caption", "story_builder", "would_you_rather", "never_have_i_ever", "mafia_lite"
        ],
    },
    "multi": {
        "title": "👥 Multiplayer",
        "games": ["matchmaking", "duel", "tournament", "team_battle", "group_challenge"],
    },
}

GAMES = {
    "dice": {"name": "🎲 Dice", "help": "Click Play. Bot rolls 1–6. Higher rolls earn better coins."},
    "coin_flip": {"name": "🪙 Coin Flip", "help": "Click Play and the bot flips Heads or Tails. Guessing is automatic."},
    "roulette": {"name": "🔫 Roulette", "help": "A safe text-only luck game. Survive the random chamber to win coins."},
    "spin_wheel": {"name": "🎡 Spin Wheel", "help": "Spin the wheel and win random coins or bonuses."},
    "jackpot": {"name": "💰 Jackpot", "help": "Try your luck. Small chance to win a large coin reward."},
    "slot_machine": {"name": "🎰 Slot Machine", "help": "Spin three symbols. Match symbols to win coins."},
    "lucky_number": {"name": "🔢 Lucky Number", "help": "Bot chooses a lucky number. If your number is close, you win."},
    "treasure_chest": {"name": "🧰 Treasure Chest", "help": "Open one mystery chest and win coins or nothing."},
    "wordriddle": {"name": "🧩 WordRiddle", "help": "Find words in an 8x8 grid. Read hints like H__ (3), then type only the word, for example: hat."},
    "hangman": {"name": "👾 Hangman", "help": "Guess letters or the full hidden word. Too many wrong guesses loses the round."},
    "scramble": {"name": "🔤 Word Scramble", "help": "Unscramble the mixed letters and type the correct word."},
    "english_puzzle": {"name": "📚 English Puzzle", "help": "Answer the grammar/vocabulary puzzle by typing the missing word."},
    "emoji_guess": {"name": "😊 Emoji Guess", "help": "Guess the word or phrase from emojis."},
    "synonym": {"name": "🟰 Synonym", "help": "Type a synonym for the given word."},
    "antonym": {"name": "↔️ Antonym", "help": "Type the opposite word."},
    "spelling": {"name": "✍️ Spelling", "help": "Type the correct spelling."},
    "rps": {"name": "✊📄✂️ RPS", "help": "Choose Rock, Paper, or Scissors with buttons."},
    "tic_tac_toe": {"name": "❌⭕ Tic Tac Toe", "help": "Play against the bot. Tap grid buttons to place X."},
    "number_battle": {"name": "🔢 Number Battle", "help": "Guess a number between 1 and 20. Closer guesses win."},
    "typing_race": {"name": "⌨️ Typing Race", "help": "Type the shown phrase exactly as fast as possible."},
    "reaction": {"name": "⚡ Reaction Test", "help": "Tap the reaction button as quickly as possible."},
    "memory_card": {"name": "🧠 Memory Card", "help": "Remember the sequence shown, then type it back."},
    "math_sprint": {"name": "➗ Math Sprint", "help": "Solve the math question and type the answer."},
    "truth_or_dare": {"name": "🔥 Truth or Dare", "help": "Bot gives a truth question or dare prompt."},
    "whoami": {"name": "🤔 Who Am I", "help": "Bot gives clues. Type the correct answer."},
    "voting_battle": {"name": "🗳️ Voting Battle", "help": "Create a quick group voting battle with inline choices."},
    "meme_caption": {"name": "😂 Meme Caption", "help": "Bot gives a meme situation. Type your funniest caption."},
    "story_builder": {"name": "📖 Story Builder", "help": "Continue the story with one sentence."},
    "would_you_rather": {"name": "🤷 Would You Rather", "help": "Choose one of two funny options."},
    "never_have_i_ever": {"name": "🙈 Never Have I Ever", "help": "Bot gives a prompt for group fun."},
    "mafia_lite": {"name": "🕵️ Mafia Lite", "help": "Lightweight group role prompt version of Mafia."},
    "matchmaking": {"name": "👥 Matchmaking", "help": "Join a queue. When another user joins, the bot creates a match."},
    "duel": {"name": "⚔️ Duel", "help": "Challenge another player in group mode. Basic duel rolls are used."},
    "tournament": {"name": "🏆 Tournament", "help": "Join or create a simple group tournament entry."},
    "team_battle": {"name": "🛡️ Team Battle", "help": "Group mini-battle. Bot randomly assigns result and rewards."},
    "group_challenge": {"name": "💬 Group Challenge", "help": "Bot posts a quick challenge for group members."},
}
