import disnake
from disnake.ext import commands
import json
import random
import os

class Colors:
    RESET = "\033[0m"  # Reset to default color
    WHITE = "\033[37m"  # White color
    GREEN = "\033[32m"  # Green color

class Towers(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.json_file_path = 'settings/towers.json'
        self.users_file_path = 'settings/userdata/users.json'

        # Ensure the configuration file exists and load it
        if not os.path.exists(self.json_file_path):
            raise FileNotFoundError(f"{self.json_file_path} not found. Please provide the configuration file.")
        
        # Initialize the users configuration file if it doesn't exist
        if not os.path.exists(self.users_file_path):
            with open(self.users_file_path, 'w') as file:
                json.dump({}, file)

    @commands.slash_command(name="towers", description="bloxflip.com/towers")
    async def towers(
        self,
        inter: disnake.ApplicationCommandInteraction,
        difficulty: str = commands.Param(choices=["easy", "medium", "hard"]),
        rows: int = commands.Param(ge=1, le=8)
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
        
        # Generate a tower location grid based on the difficulty
        grid, odds = self.generate_random_tower_location(rows, difficulty)

        # Load embed settings from JSON file
        try:
            with open(self.json_file_path, 'r') as file:
                settings = json.load(file)
        except Exception as e:
            await inter.response.send_message(f"Error loading settings: {e}")
            return
        
        embed = disnake.Embed(
            title=settings['embed_settings']['title'],
            description=settings['embed_settings']['description'].format(odds=odds, grid=grid),
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
        view.data = {"user_id": inter.user.id, "rows": rows, "difficulty": difficulty}

        # Send the embed with the buttons
        await inter.response.send_message(embed=embed, view=view)

        # Define the callback function for the reroll button
        async def reroll_callback(interaction: disnake.MessageInteraction):
            # Check if the user who clicked the button is the same as the one who executed the command
            if interaction.user.id != view.data["user_id"]:
                await interaction.response.send_message("You are not authorized to reroll this.", ephemeral=True)
                return

            # Generate a new grid and odds
            rows = view.data["rows"]
            difficulty = view.data["difficulty"]
            grid, odds = self.generate_random_tower_location(rows, difficulty)

            # Update the embed with new content
            embed.description = settings['embed_settings']['description'].format(odds=odds, grid=grid)

            # Edit the message with the updated embed
            await interaction.response.edit_message(embed=embed)

        # Add the callback to the reroll button
        reroll_button.callback = reroll_callback

    def generate_random_tower_location(self, rows, difficulty):
        # Load grid settings from JSON file
        try:
            with open(self.json_file_path, 'r') as file:
                settings = json.load(file)
        except Exception as e:
            raise Exception(f"Error loading grid settings: {e}")
        
        columns = settings['grid_settings'].get(f'columns_difficulty_{difficulty}', 3)
        total_rows = settings['grid_settings']['total_rows']

        if difficulty == "easy":
            # Calculate the odds of picking the correct columns every time
            odds = (2 / columns) ** rows * 100
        else:
            # Calculate the odds of picking the correct column every time for other difficulties
            odds = (1 / columns) ** rows * 100

        grid = []

        # Generate the specified number of rows with symbols
        for _ in range(rows):
            row = [settings['grid_settings']['mine_symbol']] * columns
            if difficulty == "easy":
                star_positions = random.sample(range(columns), 2)
            else:
                star_positions = [random.randint(0, columns - 1)]
            for pos in star_positions:
                row[pos] = settings['grid_settings']['guess_symbol']
            grid.append(row)

        # Fill the remaining rows with empty symbols
        for _ in range(total_rows - rows):
            grid.append([settings['grid_settings']['empty_symbol']] * columns)

        # Reverse the grid for display from bottom to top
        grid.reverse()

        # Format the tower location for display
        formatted_location = "```\n"
        for row in grid:
            formatted_location += '    ' + ''.join(row) + '\n'
        formatted_location += "```"

        return formatted_location, odds

def setup(bot):
    bot.add_cog(Towers(bot))
print(f'{Colors.WHITE} +{Colors.GREEN} towers.py{Colors.RESET}')
