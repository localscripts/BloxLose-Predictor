import disnake
from disnake.ext import commands

class Colors:
    RESET = "\033[0m"  # Reset to default color
    WHITE = "\033[37m"  # White color
    GREEN = "\033[32m"  # Green color

class ActivityCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        """
        Set the bot's activity to streaming with a default message when the bot is ready.
        """
        print(f'{Colors.WHITE} +{Colors.GREEN} Bot is ready. Setting activity...{Colors.RESET}')
        
        # Default activity settings
        activity_name = "Bloxlose.com"
        url = "http://bloxlose.com"  # Placeholder URL for the streaming activity
        
        # Set the bot's activity to streaming
        activity = disnake.Activity(type=disnake.ActivityType.streaming, name=activity_name, url=url)
        await self.bot.change_presence(activity=activity)
        
        print(f'{Colors.WHITE} +{Colors.GREEN} Bot is now streaming "{activity_name}" with URL {url}{Colors.RESET}')

def setup(bot):
    bot.add_cog(ActivityCog(bot))

print(f'{Colors.WHITE} +{Colors.GREEN} status.py{Colors.RESET}')
