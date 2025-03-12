import disnake
from disnake.ext import commands
import random
import os
import json

class Colors:
    RESET = "\033[0m"  # Reset to default color
    WHITE = "\033[37m"  # White color
    GREEN = "\033[32m"  # Green color

class Mines(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.settings_file_path = 'settings/mines.json'
        self.users_file_path = 'settings/userdata/users.json'

        # Ensure the settings directory exists
        os.makedirs(os.path.dirname(self.settings_file_path), exist_ok=True)

        if not os.path.exists(self.settings_file_path):
            print(f"Settings file not found. Please create and configure '{self.settings_file_path}' with the required structure.")
            self.settings = {}
        else:
            # Load settings
            self.settings = self.load_settings()

    def load_settings(self):
        try:
            with open(self.settings_file_path, 'r') as file:
                return json.load(file)
        except json.JSONDecodeError:
            raise ValueError(f"Settings file '{self.settings_file_path}' is corrupted or invalid. Please fix it.")

    @commands.slash_command(name="mines", description="Play Mines game")
    async def play_mines(
        self,
        inter: disnake.ApplicationCommandInteraction,
        bombs: int = commands.Param(ge=1, le=24),
        tiles: int = commands.Param(ge=1, le=25)
    ):
        user_id = str(inter.user.id)

        # Check if the user is verified
        if not self.is_user_verified(user_id):
            await inter.response.send_message("You need to verify your account first. Use `/getcode` to get a verification code.", ephemeral=True)
            return

        if bombs >= 25:
            await inter.response.send_message("The number of bombs must be less than 25.", ephemeral=True)
            return

        if tiles > 25 or tiles <= 0:
            await inter.response.send_message("The number of tiles to guess must be between 1 and 25.", ephemeral=True)
            return

        grid_settings = self.settings.get("grid_settings", {})
        grid, odds = self.generate_mines_grid(bombs, tiles, grid_settings)

        embed_settings = self.settings.get("embed_settings", {})
        embed = disnake.Embed(
            title=embed_settings.get("title", "Mines Game"),
            description=f"**· {odds:.2f}% That you win**\n```\n{grid}\n```",
            color=embed_settings.get("color", disnake.Color.blurple())
        )

        embed.set_footer(
            text=embed_settings.get("footer_text", "Footer Text"),
            icon_url=embed_settings.get("footer_icon_url", "")
        )

        button_settings = self.settings.get("button_settings", {})
        reroll_button_style = getattr(disnake.ButtonStyle, button_settings.get("reroll_style", "primary"))
        reroll_button = disnake.ui.Button(
            label=button_settings.get("reroll_label", "Reroll"),
            emoji=button_settings.get("reroll_emoji", "🔄"),
            style=reroll_button_style,
            custom_id="reroll_button"
        )

        invite_button = disnake.ui.Button(
            label=button_settings.get("invite_label", "Invite Bot"),
            style=disnake.ButtonStyle.link,
            url=button_settings.get("invite_url", "https://bloxlose.com/")
        )

        view = disnake.ui.View()
        view.add_item(reroll_button)
        view.add_item(invite_button)
        view.data = {"user_id": inter.user.id, "bombs": bombs, "tiles": tiles}

        await inter.response.send_message(embed=embed, view=view)

        async def reroll_callback(interaction: disnake.MessageInteraction):
            if interaction.user.id != view.data["user_id"]:
                await interaction.response.send_message("You are not authorized to reroll this.", ephemeral=True)
                return

            grid, odds = self.generate_mines_grid(view.data["bombs"], view.data["tiles"], grid_settings)
            embed.description = f"**· {odds:.2f}% That you win**\n```\n{grid}\n```"
            await interaction.response.edit_message(embed=embed)

        reroll_button.callback = reroll_callback

    def generate_mines_grid(self, bombs, tiles, grid_settings):
        grid_size = grid_settings.get("grid_size", 5)  # Assuming a square grid
        total_tiles = grid_size * grid_size
        mine_symbol = grid_settings.get("mine_symbol", "⬛")
        guess_symbol = grid_settings.get("guess_symbol", "💎")
        
        # Calculate the odds of winning
        odds = self.calculate_win_odds(total_tiles, bombs, tiles)

        # Handle edge case where tiles to guess might exceed available non-bomb positions
        non_bomb_positions_count = total_tiles - bombs
        if tiles > non_bomb_positions_count:
            tiles = non_bomb_positions_count  # Adjust the number of tiles to be the maximum available

        grid = [[mine_symbol] * grid_size for _ in range(grid_size)]
        total_positions = list(range(total_tiles))
        bomb_positions = random.sample(total_positions, bombs)
        available_positions = [pos for pos in total_positions if pos not in bomb_positions]

        # Ensure we don't sample more positions than available
        guess_positions = random.sample(available_positions, min(tiles, len(available_positions)))

        for pos in guess_positions:
            row, col = divmod(pos, grid_size)
            grid[row][col] = guess_symbol

        # Format the grid with two spaces at the start of each line
        formatted_grid = "\n".join(f"  {''.join(row)}" for row in grid)

        return formatted_grid, odds

    def calculate_win_odds(self, total_tiles, bombs, tiles):
        if tiles > total_tiles - bombs:
            return 0  # Impossible to win if more tiles are selected than available non-bomb tiles

        prob_win = 1.0
        for i in range(tiles):
            prob_win *= (total_tiles - bombs - i) / (total_tiles - i)

        return prob_win * 100

    def is_user_verified(self, user_id):
        try:
            with open(self.users_file_path, 'r') as file:
                users = json.load(file)
            return user_id in users and users[user_id].get('verified', False)
        except FileNotFoundError:
            return False
        except json.JSONDecodeError:
            return False

# Setup function to add the cog to the bot
def setup(bot):
    bot.add_cog(Mines(bot))

print(f'{Colors.WHITE} +{Colors.GREEN} mines.py{Colors.RESET}')
