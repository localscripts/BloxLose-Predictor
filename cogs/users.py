import disnake
from disnake.ext import commands
import json
import os
import asyncio

class Colors:
    RESET = "\033[0m"  # Reset to default color
    WHITE = "\033[37m"  # White color
    GREEN = "\033[32m"  # Green color

class ListVerifiedUsers(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.users_file_path = 'settings/userdata/users.json'
        self.keys_file_path = 'settings/userdata/keys.json'
        self.settings_file_path = 'settings/users.json'

        # Initialize the users configuration file if it doesn't exist
        if not os.path.exists(self.users_file_path):
            with open(self.users_file_path, 'w') as file:
                json.dump({}, file)

        # Load settings
        if not os.path.exists(self.settings_file_path):
            raise FileNotFoundError(f"{self.settings_file_path} not found. Please provide the settings file.")
        with open(self.settings_file_path, 'r') as file:
            self.settings = json.load(file)

    @commands.slash_command(name="userlist", description="Show the count of verified users and unused keys.")
    async def userlist(self, inter: disnake.ApplicationCommandInteraction):
        # Load user data
        try:
            with open(self.users_file_path, 'r') as file:
                users = json.load(file)
        except Exception as e:
            await inter.response.send_message(f"Error loading user data: {e}")
            return

        # Load key data
        try:
            with open(self.keys_file_path, 'r') as file:
                keys = json.load(file)
        except Exception as e:
            await inter.response.send_message(f"Error loading key data: {e}")
            return

        # Count verified users
        verified_count = sum(1 for user_data in users.values() if user_data.get('verified', False))

        # Extract keys used by users
        used_keys = set()
        for user_data in users.values():
            if 'key' in user_data:
                used_keys.add(user_data['key'])

        # Count unused keys
        unused_keys_count = sum(1 for key in keys.values() if key not in used_keys)

        # Count total servers and total members
        server_count = len(self.bot.guilds)
        total_members_count = sum(len(guild.members) for guild in self.bot.guilds)

        # Create the embed
        embed = disnake.Embed(
            title=self.settings['embed_settings']['title'],
            description=self.settings['embed_settings']['description'].format(
                count=verified_count,
                unused_keys=unused_keys_count,
                server_count=server_count,
                total_members_count=total_members_count
            ),
            color=self.settings['embed_settings']['color']
        )

        # Set the footer
        embed.set_footer(
            text=self.settings['embed_settings']['footer_text'],
            icon_url=self.settings['embed_settings']['footer_icon_url']
        )

        # Send the embed
        await inter.response.send_message(embed=embed)

def setup(bot):
    bot.add_cog(ListVerifiedUsers(bot))
print(f'{Colors.WHITE} +{Colors.GREEN} users.py{Colors.RESET}')
