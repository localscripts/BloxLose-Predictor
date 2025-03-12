import disnake
from disnake.ext import commands
import json
import random
import os

class Colors:
    RESET = "\033[0m"  # Reset to default color
    WHITE = "\033[37m"  # White color
    GREEN = "\033[32m"  # Green color

class Cups(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.json_file_path = 'settings/cups.json'
        self.users_file_path = 'settings/userdata/users.json'

        # Ensure the configuration file exists and load it
        if not os.path.exists(self.json_file_path):
            raise FileNotFoundError(f"{self.json_file_path} not found. Please provide the configuration file.")
        
        # Initialize the users configuration file if it doesn't exist
        if not os.path.exists(self.users_file_path):
            with open(self.users_file_path, 'w') as file:
                json.dump({}, file)

    @commands.slash_command(name="cups", description="bloxflip.com/cups")
    async def cups(
        self,
        inter: disnake.ApplicationCommandInteraction,
        cups: int = commands.Param(choices=[2, 3, 4])
    ):
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

        # Generate cups game result
        result, grid, odds = self.generate_cups_result(cups)

        # Load embed settings from JSON file
        try:
            with open(self.json_file_path, 'r') as file:
                settings = json.load(file)
        except Exception as e:
            await inter.response.send_message(f"Error loading settings: {e}")
            return

        embed = disnake.Embed(
            title=settings['embed_settings']['title'],
            description=settings['embed_settings']['description'].format(odds=odds, grid=grid, winning_cup=result),
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
        view.data = {"user_id": inter.user.id, "cups": cups}

        # Send the embed with the buttons
        await inter.response.send_message(embed=embed, view=view)

        # Define the callback function for the reroll button
        async def reroll_callback(interaction: disnake.MessageInteraction):
            # Check if the user who clicked the button is the same as the one who executed the command
            if interaction.user.id != view.data["user_id"]:
                await interaction.response.send_message("You are not authorized to reroll this.", ephemeral=True)
                return

            # Generate a new cups game result
            cups = view.data["cups"]
            result, grid, odds = self.generate_cups_result(cups)

            # Update the embed with new content
            embed.description = settings['embed_settings']['description'].format(odds=odds, grid=grid, winning_cup=result)

            # Edit the message with the updated embed
            await interaction.response.edit_message(embed=embed)

        # Add the callback to the reroll button
        reroll_button.callback = reroll_callback

    def generate_cups_result(self, cups):
        # Load cups settings from JSON file
        try:
            with open(self.json_file_path, 'r') as file:
                settings = json.load(file)
        except Exception as e:
            raise Exception(f"Error loading cups settings: {e}")
        
        cups_colors = settings['cups_settings']['cups_colors'][str(cups)]

        # Determine the winning cup
        winning_cup = random.choice(cups_colors)
        
        # Calculate odds
        odds = 100.0 / cups

        # Format the grid
        grid = "```\n"
        for color in cups_colors:
            grid += f"{color} "
        grid += "\n```"

        return winning_cup, grid, odds

def setup(bot):
    bot.add_cog(Cups(bot))
print(f'{Colors.WHITE} +{Colors.GREEN} cups.py{Colors.RESET}')
