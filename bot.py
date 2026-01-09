import discord
from discord.ext import commands
import requests
import os

# Configuration - Replace these with your actual credentials
DISCORD_TOKEN = 'your_discord_bot_token_here'
PUSHOVER_USER_KEY = 'your_pushover_user_key_here'
PUSHOVER_API_TOKEN = 'your_pushover_api_token_here'

# Optional: Restrict to specific channel IDs (leave empty list to allow all channels)
ALLOWED_CHANNELS = []  # Example: [123456789, 987654321]

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

def send_pushover(message, title="Discord Alert", priority=1, sound="pushover"):
    """
    Send a notification via Pushover
    priority: -2 to 2 (-2=lowest, -1=low, 0=normal, 1=high, 2=emergency)
    sound: pushover, bike, bugle, cashregister, classical, cosmic, falling, 
           gamelan, incoming, intermission, magic, mechanical, pianobar, 
           siren, spacealarm, tugboat, alien, climb, persistent, echo, updown, none
    """
    url = "https://api.pushover.net/1/messages.json"
    
    data = {
        "token": PUSHOVER_API_TOKEN,
        "user": PUSHOVER_USER_KEY,
        "message": message,
        "title": title,
        "priority": priority,
        "sound": sound
    }
    
    try:
        response = requests.post(url, data=data)
        return response.status_code == 200
    except Exception as e:
        print(f"Error sending Pushover notification: {e}")
        return False

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    print(f'Bot is ready to send Pushover notifications')

@bot.command(name='push')
async def push_notification(ctx, *, message: str = None):
    """
    Send a Pushover notification with loud sound
    Usage: !push (sends just a sound alert)
           !push buy btc (sends sound + message "buy btc")
    """
    # Check if channel restriction is enabled
    if ALLOWED_CHANNELS and ctx.channel.id not in ALLOWED_CHANNELS:
        await ctx.send("❌ This command is not allowed in this channel.")
        return
    
    # Get the author's name
    author = ctx.author.display_name
    
    # Create the notification message
    if message:
        notification_text = f"{author}: {message}"
        discord_response = f"✅ Push sent: **{message}**"
    else:
        notification_text = f"Alert from {author}"
        discord_response = "✅ Push notification sent!"
    
    # Always send with high priority and loud sound
    success = send_pushover(
        message=notification_text,
        title="🚨 Alert",
        priority=1,  # High priority
        sound="siren"  # Loud alert sound
    )
    
    if success:
        await ctx.send(discord_response)
    else:
        await ctx.send("❌ Failed to send push notification. Check bot logs.")

@bot.command(name='pushhelp')
async def push_help(ctx):
    """Show help for push commands"""
    help_text = """
**📱 Pushover Notification Commands**

`!push` - Send a loud alert sound
`!push <message>` - Send a loud alert sound with a message
Example: `!push btc nuking`

Everyone with Pushover will get the same loud siren sound!
    """
    await ctx.send(help_text)

# Error handling
@push_notification.error
async def push_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        # This won't trigger anymore since message is optional
        pass

# Run the bot
if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)
