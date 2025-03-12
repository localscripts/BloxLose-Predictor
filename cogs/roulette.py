import disnake
from disnake.ext import commands
import json
import random
import os

class Colors:
    RESET = "\033[0m"  # Reset to default color
    WHITE = "\033[37m"  # White color
    GREEN = "\033[32m"  # Green color
    
class Roulette(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.json_file_path = 'settings/roulette.json'
        self.users_file_path = 'settings/userdata/users.json'

        # Ensure the configuration file exists and load it
        if not os.path.exists(self.json_file_path):
            raise FileNotFoundError(f"{self.json_file_path} not found. Please provide the configuration file.")
        
        # Initialize the users configuration file if it doesn't exist
        if not os.path.exists(self.users_file_path):
            with open(self.users_file_path, 'w') as file:
                json.dump({}, file)

    @commands.slash_command(name="roulette", description="bloxflip.com/roulette")
    async def roulette(self, inter: disnake.ApplicationCommandInteraction):
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

        # Get result and odds from spinning the roulette
        result, odds = self.spin_roulette()

        # Load embed settings from JSON file
        try:
            with open(self.json_file_path, 'r') as file:
                settings = json.load(file)
        except Exception as e:
            await inter.response.send_message(f"Error loading settings: {e}")
            return

        embed = disnake.Embed(
            title=settings['embed_settings']['title'],
            description=settings['embed_settings']['description'].format(odds=odds, grid=result),
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

            # Generate a new grid and odds
            result, odds = self.spin_roulette()

            # Update the embed with new content
            embed.description = settings['embed_settings']['description'].format(odds=odds, grid=result)

            # Edit the message with the updated embed
            await interaction.response.edit_message(embed=embed)

        # Add the callback to the reroll button
        reroll_button.callback = reroll_callback

    def spin_roulette(self):
        # Load roulette settings from JSON file
        try:
            with open(self.json_file_path, 'r') as file:
                settings = json.load(file)
        except Exception as e:
            raise Exception(f"Error loading roulette settings: {e}")
        
        colors = settings['roulette_settings']['colors']
        chosen_color = random.choices(colors, weights=[entry['odds'] for entry in colors], k=1)[0]
        chosen_symbol = chosen_color['symbol']

        # Construct the grid based on the chosen color
        red_symbol = next(color['symbol'] for color in colors if color['color'] == "Red")
        purple_symbol = next(color['symbol'] for color in colors if color['color'] == "Purple")
        yellow_symbol = next(color['symbol'] for color in colors if color['color'] == "Yellow")

        if chosen_symbol == yellow_symbol:
            result_grid = f"🟥🟪🟥🟪[{yellow_symbol}]🟥🟪🟥🟪"
        elif chosen_symbol == red_symbol:
            result_grid = f"🟥🟪🟥🟪[{red_symbol}]🟪🟥🟪🟥"
        elif chosen_symbol == purple_symbol:
            result_grid = f"🟪🟥🟪🟥[{purple_symbol}]🟥🟪🟥🟪"

        # Wrap the result grid in a code block
        result_grid = f"```\n{result_grid}\n```"

        odds = chosen_color['odds']

        return result_grid, odds

def setup(bot):
    bot.add_cog(Roulette(bot))
print(f'{Colors.WHITE} +{Colors.GREEN} roulette.py{Colors.RESET}')
