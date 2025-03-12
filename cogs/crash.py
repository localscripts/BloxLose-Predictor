import disnake
from disnake.ext import commands
import json
import random
import os

class Colors:
    RESET = "\033[0m"  # Reset to default color
    WHITE = "\033[37m"  # White color
    GREEN = "\033[32m"  # Green color

class Crash(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.json_file_path = 'settings/crash.json'
        self.users_file_path = 'settings/userdata/users.json'

        # Ensure the configuration file exists and load it
        if not os.path.exists(self.json_file_path):
            raise FileNotFoundError(f"{self.json_file_path} not found. Please provide the configuration file.")
        
        # Initialize the users configuration file if it doesn't exist
        if not os.path.exists(self.users_file_path):
            with open(self.users_file_path, 'w') as file:
                json.dump({}, file)

    @commands.slash_command(name="crash", description="bloxflip.com/crash")
    async def crash(self, inter: disnake.ApplicationCommandInteraction):
        user_id = str(inter.user.id)

        # Check if the user is verified
        try:
            with open(self.users_file_path, 'r') as file:
                users = json.load(file)
        except Exception as e:
            await inter.response.send_message(f"Error loading user data: {e}")
            return

        if user_id not in users or not isinstance(users[user_id], dict) or not users[user_id].get('verified', False):
            await inter.response.send_message("You need to verify your account first. Use `/getcode` to get a verification code.")
            return

        # Generate crash game result
        multiplier, odds = self.generate_crash_result()

        # Load embed settings from JSON file
        try:
            with open(self.json_file_path, 'r') as file:
                settings = json.load(file)
        except Exception as e:
            await inter.response.send_message(f"Error loading settings: {e}")
            return

        embed = disnake.Embed(
            title=settings['embed_settings']['title'],
            description=settings['embed_settings']['description'].format(odds=odds, multiplier=multiplier),
            color=settings['embed_settings']['color']
        )

        # Set the footer
        embed.set_footer(
            text=settings['embed_settings']['footer_text'],
            icon_url=settings['embed_settings']['footer_icon_url']
        )

        # Create the reroll button
        reroll_button = disnake.ui.Button(
            label=settings['button_settings']['reroll_label'],
            emoji=settings['button_settings']['reroll_emoji'],
            style=disnake.ButtonStyle[settings['button_settings']['reroll_style'].lower()],
            custom_id="reroll_button"
        )

        # Create the invite bot button
        invite_button = disnake.ui.Button(
            label=settings['button_settings']['invite_label'],
            style=disnake.ButtonStyle.link,
            url=settings['button_settings']['invite_url']
        )

        # Create the view for the buttons
        view = disnake.ui.View()
        view.add_item(reroll_button)
        view.add_item(invite_button)

        # Store the user ID in the interaction
        view.data = {"user_id": inter.user.id}

        # Send the embed with the buttons
        await inter.response.send_message(embed=embed, view=view)

        # Define the callback function for the reroll button
        async def reroll_callback(interaction: disnake.MessageInteraction):
            # Check if the user who clicked the button is the same as the one who executed the command
            if interaction.user.id != view.data["user_id"]:
                await interaction.response.send_message("You are not authorized to reroll this.", ephemeral=True)
                return

            # Generate a new crash game result
            multiplier, odds = self.generate_crash_result()

            # Update the embed with new content
            embed.description = settings['embed_settings']['description'].format(odds=odds, multiplier=multiplier)

            # Edit the message with the updated embed
            await interaction.response.edit_message(embed=embed)

        # Add the callback to the reroll button
        reroll_button.callback = reroll_callback

    def generate_crash_result(self):
        # Load crash settings from JSON file
        try:
            with open(self.json_file_path, 'r') as file:
                settings = json.load(file)
        except Exception as e:
            raise Exception(f"Error loading crash settings: {e}")
        
        max_multiplier = settings['crash_settings']['max_multiplier']
        increment_chance = settings['crash_settings']['increment_chance']
        crash_chance = settings['crash_settings']['crash_chance']

        multiplier = 1.0
        while random.random() < increment_chance and multiplier < max_multiplier:
            multiplier += 0.01

        odds = (1 / multiplier) * 100

        return round(multiplier, 2), odds

def setup(bot):
    bot.add_cog(Crash(bot))
print(f'{Colors.WHITE} +{Colors.GREEN} crash.py{Colors.RESET}')
