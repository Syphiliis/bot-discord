# Nullshot Verification Bot

A professional, UI-based Discord bot for verifying users via email whitelist.

## Features
- **Modern UI**: Uses a permanent "Verify Account" button and a pop-up form (Modal).
- **Admin Tools**:
    - Manage whitelist from Discord: `/admin add` and `/admin remove`.
    - Auto-setup: `/setup` creates the private `#admin-logs` channel and posts the verification panel.
- **Security**: Restricted admin commands protected by Role ID checking.

## Prerequisites
1.  **Python 3.8+**: [Download](https://www.python.org/downloads/)
2.  **Libraries**: `pip install discord.py python-dotenv`

## Configuration (.env)
Create a `.env` file:

```env
BOT_TOKEN=your_token_here
ROLE_ID=123456789 (Role given to verified users)
GUILD_ID=987654321 (Your Server ID)
ADMIN_ROLE_ID=111222333 (Role ID for admins allow to use /admin and /setup)
```

## How to Run

1.  Start the bot:
    ```bash
    python bot.py
    ```
2.  **First Time Setup**:
    - Go to the channel where you want users to verify.
    - Run `/setup`.
    - Result:
        - The bot posts the "Nullshot Verification" embed with the Button.
        - The bot creates `#admin-logs` (visible only to Bot & Admins).

## Commands

- **User**:
    - `[Click Button]`: Opens verification form.
- **Admin** (Requires `ADMIN_ROLE_ID`):
    - `/admin add [email]`: Add an email to the whitelist.
    - `/admin remove [email]`: Remove an email.
    - `/setup`: Deploy the bot interface.
