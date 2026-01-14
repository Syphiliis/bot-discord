import discord
from discord import app_commands
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ==========================================
# CONFIGURATION SECTION
# ==========================================

# 1. Your Bot Token
BOT_TOKEN = os.getenv('BOT_TOKEN')

# 2. The ID of the role to assign on success
# Convert to int if exists, else None
ROLE_ID = int(os.getenv('ROLE_ID')) if os.getenv('ROLE_ID') else None

# 3. Your Server (Guild) ID
# Required to sync commands instantly. If None, commands sync globally (can take 1 hour).
GUILD_ID = int(os.getenv('GUILD_ID')) if os.getenv('GUILD_ID') else None


# 4. File Names
EMAILS_FILE = 'emails.txt'
USED_EMAILS_FILE = 'used_emails.txt'

# ==========================================
# BOT SETUP
# ==========================================

# ==========================================
# LOGGING SETUP
# ==========================================
import logging

# Configure logging to output to console with timestamps
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)


# Define Intents
intents = discord.Intents.default()
# 'members' is needed to assign roles
intents.members = True 

class VerifyClient(discord.Client):
    def __init__(self):
        super().__init__(intents=intents)
        # Separate CommandTree for slash commands
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        """
        This is called when the bot starts. We use it to sync commands.
        """
        if GUILD_ID:
            guild = discord.Object(id=GUILD_ID)
            # Copy global commands to this guild
            self.tree.copy_global_to(guild=guild)
            # Sync to the guild
            await self.tree.sync(guild=guild)
            logging.info(f"Commands synced to Guild ID: {GUILD_ID}")
        else:
            # Sync globally (might take time)
            await self.tree.sync()
            logging.info("Commands synced globally.")


client = VerifyClient()

# ==========================================
# FILE OPERATIONS
# ==========================================

def load_emails(filename):
    if not os.path.exists(filename):
        logging.warning(f"File {filename} not found. Returning empty set.")
        return set()
    with open(filename, 'r', encoding='utf-8') as f:
        return {line.strip().lower() for line in f if line.strip()}

def append_used_email(email):
    try:
        with open(USED_EMAILS_FILE, 'a', encoding='utf-8') as f:
            f.write(f"{email}\n")
    except Exception as e:
        logging.error(f"Failed to save used email {email}: {e}")

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
        append_used_email(email_cleaned)
        
        logging.info(f"SUCCESS - Role Assigned | User: {user_desc} | Email: {email_cleaned}")
        await interaction.response.send_message(
            f"✅ Success! You have been verified and granted the **{role.name}** role.",
            ephemeral=True
        )

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
    logging.info(f'Target Role ID: {ROLE_ID}')

if __name__ == '__main__':
    if BOT_TOKEN == 'YOUR_BOT_TOKEN_HERE':
        print("ERROR: Please set the BOT_TOKEN in the script configuration.")
    else:
        try:
            client.run(BOT_TOKEN)
        except Exception as e:
            print(f"ERROR: {e}")
