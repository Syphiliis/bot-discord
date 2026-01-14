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

## Step 1: Configure the Bot (Bot Tab)

1.  Go to the [Discord Developer Portal](https://discord.com/developers/applications) and click on your application.
2.  On the left sidebar, click **"Bot"**.
3.  **Privileged Gateway Intents** (Scroll down to this section):
    *   [x] **Presence Intent**: (Optional, leave unchecked)
    *   [x] **Server Members Intent**: **CHECK THIS** (Required to give roles).
    *   [x] **Message Content Intent**: **CHECK THIS** (Recommended for future features).
    *   Click **"Save Changes"** at the bottom.
4.  **Token**:
    *   Click **"Reset Token"**.
    *   Copy the long string of characters. This is your `BOT_TOKEN`.

## Step 2: Create Invite Link (OAuth2 Tab)

1.  On the left sidebar, click on **"OAuth2"**.
2.  If you see a sub-menu under OAuth2, click **"URL Generator"**. If not, scroll down to the **"OAuth2 URL Generator"** section on the main OAuth2 page.
3.  **Scopes** (This is a large grid of checkboxes):
    *   Find and check **`bot`** (This makes the Bot Permissions section appear).
    *   Find and check **`applications.commands`** (Required for `/beta`).
4.  **Bot Permissions** (This section appears BELOW the Scopes grid after you check `bot`):
    *   Under "General Permissions", check **`Manage Roles`**.
    *   Under "Text Permissions", check **`View Channels`** and **`Send Messages`**.
5.  **Generated URL**:
    *   Scroll to the very bottom of the page.
    *   Copy the URL in the "Generated URL" field.
    *   Paste this URL into a new browser tab to invite the bot to your server.

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
