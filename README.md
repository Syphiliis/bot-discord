# Discord Verification Bot (Email Based)

A Discord bot that assigns a role to users who verify their email address via a Slash Command `/verify`.

## Features
- **Slash Command**: `/verify [email]` (Hidden/Ephemeral response)
- **Whitelist**: Checks against `emails.txt`.
- **One-time Use**: Tracks used emails in `used_emails.txt` to prevent multiple accounts using the same email.

## Prerequisites

1.  **Python 3.8+**: [Download](https://www.python.org/downloads/)
2.  **discord.py**: `pip install discord.py`

## Step 1: Configure the Bot (Bot Tab)

1.  On the left sidebar, click **"Bot"**.
2.  **Privileged Gateway Intents** (Scroll down to this section):
    *   [x] **Presence Intent**: (Optional, leave unchecked)
    *   [x] **Server Members Intent**: **CHECK THIS** (Required to give roles).
    *   [x] **Message Content Intent**: **CHECK THIS** (Recommended for future features).
    *   Click **"Save Changes"** at the bottom.
3.  **Bot Permissions** (Calculator):
    *   **IGNORE** the permissions calculator on this specific page. We will set permissions in the next step.
4.  **Token**:
    *   Click **"Reset Token"**.
    *   Copy the long string of characters. This is your `BOT_TOKEN`.
    *   Paste it into your `bot.py` file immediately.

## Step 2: Create Invite Link (OAuth2 Tab)

1.  On the left sidebar, click on **"OAuth2"**.
2.  If you see a sub-menu under OAuth2, click **"URL Generator"**. If not, scroll down to the **"OAuth2 URL Generator"** section on the main OAuth2 page.
3.  **Scopes** (This is a large grid of checkboxes):
    *   Find and check **`bot`** (This makes the Bot Permissions section appear).
    *   Find and check **`applications.commands`** (Required for `/verify`).
4.  **Bot Permissions** (This section appears BELOW the Scopes grid after you check `bot`):
    *   Under "General Permissions", check **`Manage Roles`**.
    *   Under "Text Permissions", check **`View Channels`** and **`Send Messages`**.
5.  **Generated URL**:
    *   Scroll to the very bottom of the page.
    *   Copy the URL in the "Generated URL" field.
    *   Paste this URL into a new browser tab to invite the bot to your server.

1.  Open `bot.py` and set:
    - `BOT_TOKEN`: Your bot token.
    - `GUILD_ID`: Your Server ID (Right-click Server Name -> Copy ID). **Required for instant command syncing.**
    - `ROLE_ID`: The Role ID to give (Right-click Role -> Copy ID).
    - Ensure your Bot's Role is **higher** than the role it assigns in the server settings.

## Step 3: Manage Data

1.  **`emails.txt`**: Add allowed emails, one per line.
2.  **`used_emails.txt`**: Leave empty or manage manually if you want to reset a user.

## Step 4: Run

```bash
python bot.py
```

Wait until you see "Commands synced...". Then in Discord, type `/` and you should see `/verify`.
