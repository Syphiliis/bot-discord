import discord
from discord import app_commands
from discord import ui
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
# UI COMPONENTS (MODAL & VIEW)
# ==========================================

class VerificationModal(ui.Modal, title='Nullshot Verification'):
    email_input = ui.TextInput(
        label='Enter your Email Address',
        placeholder='you@example.com',
        required=True,
        style=discord.TextStyle.short
    )

    async def on_submit(self, interaction: discord.Interaction):
        # 1. Sanitize
        email = self.email_input.value.strip().lower()
        user = interaction.user
        user_desc = f"{user.name}#{user.discriminator} (ID: {user.id})"

        logging.info(f"Verification Attempt - User: {user_desc} | Email: {email}")

        # 2. Load Data
        whitelisted_emails = load_emails(EMAILS_FILE)
        used_emails = load_emails(USED_EMAILS_FILE)

        # 3. Logic
        if email in used_emails:
            logging.warning(f"FAILED - Email used | User: {user_desc} | Email: {email}")
            await interaction.response.send_message(
                f"❌ Error: The email `{email}` has already been used.", ephemeral=True
            )
            return

        if email not in whitelisted_emails:
            logging.warning(f"FAILED - Not Whitelisted | User: {user_desc} | Email: {email}")
            await interaction.response.send_message(
                f"❌ Error: The email `{email}` is not in the allowed list.", ephemeral=True
            )
            return

        # 4. Success
        role = interaction.guild.get_role(ROLE_ID)
        if not role:
            logging.critical(f"FAILED - Role {ROLE_ID} missing")
            await interaction.response.send_message("❌ Configuration Error: Role not found.", ephemeral=True)
            return

        try:
            await user.add_roles(role)
            save_email(USED_EMAILS_FILE, email)
            logging.info(f"SUCCESS - Role Assigned | User: {user_desc} | Email: {email}")
            
            await interaction.response.send_message(
                f"✅ Success! You have been verified and granted the **{role.name}** role.", ephemeral=True
            )
            
            # 5. Log to #admin-logs channel
            log_channel = discord.utils.get(interaction.guild.channels, name=LOG_CHANNEL_NAME)
            if log_channel:
                await log_channel.send(f"✅ **Verified**: {user.mention} (`{user.id}`) used email `{email}`.")

        except discord.Forbidden:
            logging.error(f"FAILED - Forbidden for {user_desc}")
            await interaction.response.send_message("❌ Error: I don't have permission to assign that role.", ephemeral=True)
        except Exception as e:
            logging.error(f"FAILED - Error for {user_desc}: {e}")
            await interaction.response.send_message("❌ Unexpected error.", ephemeral=True)

class VerificationView(ui.View):
    def __init__(self):
        super().__init__(timeout=None) # Persistent view

    @ui.button(label='Verify Account', style=discord.ButtonStyle.green, custom_id='verify_button')
    async def verify(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.send_modal(VerificationModal())

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
        # Add the persistent view so it works after restart
        self.add_view(VerificationView())
        
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
# ADMIN COMMANDS
# ==========================================

def is_admin(interaction: discord.Interaction):
    if not ADMIN_ROLE_ID:
        return False
    return interaction.user.get_role(ADMIN_ROLE_ID) is not None

@client.tree.command(name="setup", description="[Admin] Create log channel and post verification panel.")
async def setup(interaction: discord.Interaction):
    if not is_admin(interaction):
        await interaction.response.send_message("❌ You are not an admin.", ephemeral=True)
        return

    # 1. Create Log Channel
    guild = interaction.guild
    existing_channel = discord.utils.get(guild.channels, name=LOG_CHANNEL_NAME)
    
    if not existing_channel:
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            guild.me: discord.PermissionOverwrite(read_messages=True),
            # Add Admin Role permissions
            guild.get_role(ADMIN_ROLE_ID): discord.PermissionOverwrite(read_messages=True)
        }
        try:
            await guild.create_text_channel(LOG_CHANNEL_NAME, overwrites=overwrites)
            msg_channel = f"✅ Created channel `#{LOG_CHANNEL_NAME}`."
        except Exception as e:
            msg_channel = f"⚠️ Could not create channel: {e}"
    else:
        msg_channel = f"ℹ️ Channel `#{LOG_CHANNEL_NAME}` already exists."

    # 2. Post Panel
    embed = discord.Embed(
        title="Nullshot Verification",
        description="Click the button below to verify your account and gain access.",
        color=discord.Color.blue()
    )
    await interaction.channel.send(embed=embed, view=VerificationView())
    
    await interaction.response.send_message(f"{msg_channel}\n✅ Verification panel posted.", ephemeral=True)

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

@client.event
async def on_ready():
    logging.info(f'Logged in as {client.user}')
    if not ADMIN_ROLE_ID:
        logging.warning("⚠️ ADMIN_ROLE_ID is 0! Admin commands will not work.")

if __name__ == '__main__':
    client.run(BOT_TOKEN)
