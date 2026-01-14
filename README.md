# Discord Verification Bot (Email Based)

A Discord bot that assigns a role to users who verify their email address via a Slash Command `/beta`.

## Features
- **Slash Command**: `/beta [email]` (Hidden/Ephemeral response)
- **Whitelist**: Checks against `emails.txt`.
- **One-time Use**: Tracks used emails in `used_emails.txt` to prevent multiple accounts using the same email.
- **Secure Config**: Uses `.env` file for sensitive tokens.

## Prerequisites

1.  **Python 3.8+**: [Download](https://www.python.org/downloads/)
2.  **Required Libraries**: 
    ```bash
    pip install discord.py python-dotenv
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

## Step 3: Configuration (.env)

1.  Create a file named `.env` in the same folder as `bot.py`.
2.  Add your secrets inside it like this:

    ```env
    BOT_TOKEN=paste_your_token_here
    ROLE_ID=123456789
    GUILD_ID=987654321
    ```

3.  **Explanation**:
    - `BOT_TOKEN`: Your bot token from Step 1.
    - `ROLE_ID`: Right-click the Role in discord -> Copy ID.
    - `GUILD_ID`: Right-click the Server Name -> Copy ID.

## Step 4: Manage Data

1.  **`emails.txt`**: Add allowed emails, one per line.
2.  **`used_emails.txt`**: Leave empty or manage manually if you want to reset a user.

## Step 5: Run

```bash
python bot.py
```

Wait until you see "Commands synced...". Then in Discord, type `/` and you should see `/beta`.
