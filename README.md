# Discord Verification Bot (Email Based)

A Discord bot that assigns a role to users who verify their email address via a Slash Command `/beta`.

## Features
- **Slash Command**: `/beta [email]` (Hidden/Ephemeral response)
- **Admin Commands**: 
    - `/admin add [email]`
    - `/admin remove [email]`
- **Logging**:
    - Console logs.
    - Post success messages to `#admin-logs` (if channel exists).
- **Security**: 
    - Uses `.env` for secrets.
    - Admin commands protected by `ADMIN_ROLE_ID`.

## Prerequisites

1.  **Python 3.8+**: [Download](https://www.python.org/downloads/)
2.  **Required Libraries**: 
    ```bash
    pip install -r requirements.txt
    ```

## Configuration (.env)

Create a `.env` file:

```env
BOT_TOKEN=your_token_here
ROLE_ID=123456789 (Role given to verified users)
GUILD_ID=987654321 (Your Server ID)
ADMIN_ROLE_ID=111222333 (Role ID allowed to use /admin commands)
```

## Setup Log Channel

Create a text channel named `admin-logs` in your server. Make it private so only Admins and the Bot can see it. The bot will automatically post verification success messages there.

## Commands

- **User**:
    - `/beta [email]`: Verify account.
- **Admin** (Requires `ADMIN_ROLE_ID`):
    - `/admin add [email]`: Add an email to the whitelist.
    - `/admin remove [email]`: Remove an email.

## How to Run

```bash
python bot.py
```
