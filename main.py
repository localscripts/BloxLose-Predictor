import disnake
from disnake.ext import commands
import asyncio
import os

# Define color codes
class Colors:
    RESET = "\033[0m"  # Reset to default color
    GREY = "\033[90m"  # Grey color
    BLUE = "\033[34m"  # Blue color
    YELLOW = "\033[33m"  # Yellow color
    LIGHT_BLUE = "\033[94m"  # Light blue color
    DARK_BLUE = "\033[34m"  # Dark blue color
    MAGENTA = "\033[35m"  # Magenta color

def gradient(start_color, end_color, steps):
    """Generate a gradient of colors between start_color and end_color."""
    start_r, start_g, start_b = start_color
    end_r, end_g, end_b = end_color
    gradient_colors = []
    for i in range(steps):
        ratio = i / (steps - 1)
        r = int(start_r + (end_r - start_r) * ratio)
        g = int(start_g + (end_g - start_g) * ratio)
        b = int(start_b + (end_b - start_b) * ratio)
        gradient_colors.append((r, g, b))
    return gradient_colors

def print_gradient(text, start_color, end_color, steps):
    """Print text with a gradient color effect."""
    gradient_colors = gradient(start_color, end_color, steps)
    chunk_size = max(1, len(text) // steps)  # Ensure at least 1 character per chunk
    for i in range(steps):
        color = gradient_colors[i]
        print(f"\033[38;2;{color[0]};{color[1]};{color[2]}m{text[i*chunk_size:(i+1)*chunk_size]}{Colors.RESET}", end='')
    print()  # New line after gradient

intents = disnake.Intents.default()
intents.messages = True
intents.message_content = True
intents.guilds = True
intents.members = True  # Add this line to enable member-related events and fetch member list

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    # Print colored "Logged in as" message
    print(f'{Colors.GREY}Logged in as {Colors.BLUE}{bot.user.name}{Colors.RESET}')
    
    # Load extensions
    try:
        bot.load_extension('cogs.roulette')
        bot.load_extension('cogs.towers')
        bot.load_extension('cogs.verify')
        bot.load_extension('cogs.mines')
        bot.load_extension('cogs.crash')
        bot.load_extension('cogs.users')
        bot.load_extension('cogs.cups')
        bot.load_extension('cogs.dice')

        # Print gradient text from light blue to dark blue
        print_gradient("[ Cogs loaded successfully ]", (173, 216, 230), (0, 0, 139), 30)
    except Exception as e:
        print(f"Failed to load extension: {e}")

    # Set the bot's activity to streaming
    activity_name = "BloxLose.com"
    url = "https://www.twitch.tv/ohnepixel"  # Replace with an actual Twitch URL if needed
    activity = disnake.Activity(type=disnake.ActivityType.streaming, name=activity_name, url=url)
    await bot.change_presence(activity=activity)

    # Print activity to debug
    print(f'{Colors.YELLOW}Setting activity to: {activity.type.name.capitalize()} - "{activity.name}"{Colors.RESET}')
    
    # Fetch the updated cache
    server_count = len(bot.guilds)
    members_set = set()
    
    for guild in bot.guilds:
        for member in guild.members:
            members_set.add(member.id)  # Using member.id to ensure uniqueness
        
        # Create an invite link if possible
        invite_link = "N/A"
        for channel in guild.text_channels:
            if channel.permissions_for(guild.me).create_instant_invite:
                try:
                    invite = await channel.create_invite(max_age=3600, max_uses=0)  # Invite lasts for 1 hour
                    invite_link = invite.url
                except disnake.Forbidden:
                    invite_link = "Missing Permissions"
                break

        # Print the server name, number of users, and invite link
        print(f'Server: {guild.name} | Users: {len(guild.members)} | Invite: {invite_link}')
        
        # Delay to avoid rate limiting
        await asyncio.sleep(1)  # Delay for 1 second

    unique_members_count = len(members_set)
    # Print gradient text for server count message
    print_gradient(f' > The bot is in {server_count} servers with {unique_members_count} unique members.', (255, 255, 0), (255, 215, 0), 30)  # Gradient from yellow to gold

if __name__ == "__main__":
    bot_token = "PUTURTOKEN"
    bot.run(bot_token)
