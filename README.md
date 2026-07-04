# Telegram Advanced Gaming Bot — Full Working Code

This is a working Telegram gaming bot project with MongoDB, inline button menus, shop, admin treasury, logs, WordRiddle, and a futuristic admin web panel.

## Important security note
You previously pasted a MongoDB URI publicly. Rotate/change that MongoDB database password before running this project.

## Features included

- `/start`, `/help`, `/profile`, `/games`, `/top`
- Inline button game hub
- 30+ playable mini-games / activities
- Works in DM and groups
- MongoDB user registration
- Coins, wins, losses, streaks
- Daily reward
- Shop with inventory
- User spending goes to Admin Treasury
- Transaction logs and admin logs
- Futuristic admin login page
- Admin dashboard with users, coins, treasury, shop, games, tournaments, logs, settings
- WordRiddle 8x8 grid with word-only answers, no `/guess`

## Install

```bash
pip install -r requirements.txt
```

## Configure

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Edit `.env` and add your values:

```env
BOT_TOKEN=your_bot_token
MONGO_URI=your_new_mongodb_uri
ADMIN_USERNAME=admin
ADMIN_PASSWORD=your_admin_password
```

## Run the bot

```bash
python run_bot.py
```

## Run the admin panel

```bash
python run_web.py
```

Open:

```text
http://127.0.0.1:5000
```

## Main bot UX

Users mostly use buttons:

```text
/start
/games
/profile
/help
/top
```

`/games` opens the inline game hub.

## Game categories

- Luck Games
- Word Games
- Competitive Games
- Fun Group Games
- Multiplayer / Tournament
- Shop

## WordRiddle

User clicks WordRiddle in the menu. The bot sends an 8x8 grid and hints like:

```text
H__ (3)
C__ (3)
```

The user only types the word:

```text
hat
```

No `/guess` command is used.

## Admin panel

Tabs:

- Dashboard
- Users
- Coins
- Treasury
- Shop
- Games
- Tournaments
- Logs
- Settings

Admin can add/remove coins, add coins to everyone, ban/unban users, view logs, and see treasury.
