import discord
from discord import app_commands
import os
from dotenv import load_dotenv
import logging

# Load environment variables from .env file
load_dotenv()

# ==========================================
# CONFIGURATION SECTION
# ==========================================

BOT_TOKEN = os.getenv('BOT_TOKEN')
ROLE_ID = int(os.getenv('ROLE_ID')) if os.getenv('ROLE_ID') else None
GUILD_ID = int(os.getenv('GUILD_ID')) if os.getenv('GUILD_ID') else None
ADMIN_ROLE_ID = int(os.getenv('ADMIN_ROLE_ID')) if os.getenv('ADMIN_ROLE_ID') else None

EMAILS_FILE = 'emails.txt'
USED_EMAILS_FILE = 'used_emails.txt'
LOG_CHANNEL_NAME = 'admin-logs'

# ==========================================
# LOGGING SETUP
# ==========================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# ==========================================
# BOT SETUP
# ==========================================

intents = discord.Intents.default()
intents.members = True

class NullshotBot(discord.Client):
    def __init__(self):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        if GUILD_ID:
            guild = discord.Object(id=GUILD_ID)
            self.tree.copy_global_to(guild=guild)
            await self.tree.sync(guild=guild)
            logging.info(f"Commands synced to Guild ID: {GUILD_ID}")
        else:
            await self.tree.sync()
            logging.info("Commands synced globally.")

client = NullshotBot()

# ==========================================
# FILE OPERATIONS
# ==========================================

def load_emails(filename):
    if not os.path.exists(filename):
        logging.warning(f"File {filename} not found. Returning empty set.")
        return set()
    with open(filename, 'r', encoding='utf-8') as f:
        return {line.strip().lower() for line in f if line.strip()}

def save_email(filename, email):
    try:
        with open(filename, 'a', encoding='utf-8') as f:
            f.write(f"{email}\n")
    except Exception as e:
        logging.error(f"Failed to save email {email} to {filename}: {e}")

def remove_email_from_file(filename, email_to_remove):
    if not os.path.exists(filename):
        return False
    
    lines = []
    found = False
    with open(filename, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip().lower() == email_to_remove.lower():
                found = True
            else:
                lines.append(line)
    
    if found:
        with open(filename, 'w', encoding='utf-8') as f:
            f.writelines(lines)
    return found

# ==========================================
# ADMIN COMMANDS
# ==========================================

def is_admin(interaction: discord.Interaction):
    if not ADMIN_ROLE_ID:
        return False
    return interaction.user.get_role(ADMIN_ROLE_ID) is not None

@client.tree.command(name="admin", description="Manage the whitelist.")
@app_commands.describe(action="add/remove", email="The email to manage")
@app_commands.choices(action=[
    app_commands.Choice(name="Add Email", value="add"),
    app_commands.Choice(name="Remove Email", value="remove")
])
async def admin(interaction: discord.Interaction, action: app_commands.Choice[str], email: str):
    if not is_admin(interaction):
        await interaction.response.send_message("❌ You are not an admin.", ephemeral=True)
        return

    email = email.lower().strip()
    
    if action.value == "add":
        whitelisted = load_emails(EMAILS_FILE)
        if email in whitelisted:
            await interaction.response.send_message(f"⚠️ `{email}` is already in the whitelist.", ephemeral=True)
        else:
            save_email(EMAILS_FILE, email)
            await interaction.response.send_message(f"✅ Added `{email}` to whitelist.", ephemeral=True)
            logging.info(f"ADMIN ADD - {interaction.user} added {email}")
            
    elif action.value == "remove":
        removed = remove_email_from_file(EMAILS_FILE, email)
        if removed:
            await interaction.response.send_message(f"✅ Removed `{email}` from whitelist.", ephemeral=True)
            logging.info(f"ADMIN REMOVE - {interaction.user} removed {email}")
        else:
            await interaction.response.send_message(f"⚠️ `{email}` was not found in whitelist.", ephemeral=True)

# ==========================================
# SLASH COMMANDS
# ==========================================

@client.tree.command(name="beta", description="Verify your email to get access.")
@app_commands.describe(email="Your email address")
async def beta(interaction: discord.Interaction, email: str):
    """
    Slash command /beta [email]
    """
    user = interaction.user
    user_desc = f"{user.name}#{user.discriminator} (ID: {user.id})"
    
    # 1. Sanitize Input
    email_cleaned = email.strip().lower()
    
    # 2. Load Data (Live reloading)
    whitelisted_emails = load_emails(EMAILS_FILE)
    used_emails = load_emails(USED_EMAILS_FILE)
    
    logging.info(f"Verification Attempt - User: {user_desc} | Email: {email_cleaned}")
    
    # 3. Validation Logic
    if email_cleaned in used_emails:
        logging.warning(f"FAILED - Email already used | User: {user_desc} | Email: {email_cleaned}")
        await interaction.response.send_message(
            f"❌ Error: The email `{email_cleaned}` has already been used.", 
            ephemeral=True
        )
        return

    if email_cleaned not in whitelisted_emails:
        logging.warning(f"FAILED - Email not in whitelist | User: {user_desc} | Email: {email_cleaned}")
        await interaction.response.send_message(
            f"❌ Error: The email `{email_cleaned}` is not in the allowed list.", 
            ephemeral=True
        )
        return

    # 4. Success Case
    guild = interaction.guild
    if not guild:
        logging.error(f"FAILED - Command used outside of guild | User: {user_desc}")
        await interaction.response.send_message("❌ Error: This command must be used in a server.", ephemeral=True)
        return

    role = guild.get_role(ROLE_ID)
    if not role:
        logging.critical(f"FAILED - Configuration Error: Role ID {ROLE_ID} not found in guild.")
        await interaction.response.send_message(f"❌ Error: Configured Role ID {ROLE_ID} not found.", ephemeral=True)
        return

    try:
        # Assign the role
        await user.add_roles(role)
        
        # Mark email as used
        save_email(USED_EMAILS_FILE, email_cleaned)
        
        logging.info(f"SUCCESS - Role Assigned | User: {user_desc} | Email: {email_cleaned}")
        await interaction.response.send_message(
            f"✅ Success! You have been verified and granted the **{role.name}** role.",
            ephemeral=True
        )

        # 5. Log to #admin-logs channel
        log_channel = discord.utils.get(interaction.guild.channels, name=LOG_CHANNEL_NAME)
        if log_channel:
            try:
                await log_channel.send(f"✅ **Verified**: {user.mention} (`{user.id}`) used email `{email_cleaned}`.")
            except Exception as e:
                logging.error(f"Could not send to log channel: {e}")

    except discord.Forbidden:
        logging.error(f"FAILED - Permission Error | Bot cannot assign role {role.name} to {user_desc}. Check role hierarchy.")
        await interaction.response.send_message(
            "❌ Error: I do not have permission to assign that role. Please contact an admin.",
            ephemeral=True
        )
    except Exception as e:
        logging.error(f"FAILED - Unexpected Error for {user_desc}: {e}")
        await interaction.response.send_message(
            f"❌ An unexpected error occurred: {e}",
            ephemeral=True
        )

@client.event
async def on_ready():
    logging.info(f'Logged in as {client.user} (ID: {client.user.id})')
    logging.info('------')
    if GUILD_ID:
        logging.info(f'Operating in Guild ID: {GUILD_ID}')
    if not ADMIN_ROLE_ID:
        logging.warning("⚠️ ADMIN_ROLE_ID is 0! Admin commands will not work.")
    logging.info(f'Target Role ID: {ROLE_ID}')

if __name__ == '__main__':
    client.run(BOT_TOKEN)
