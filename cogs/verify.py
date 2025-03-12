import disnake
from disnake.ext import commands
import json
import os

class Colors:
    RESET = "\033[0m"  # Reset to default color
    WHITE = "\033[37m"  # White color
    GREEN = "\033[32m"  # Green color

class Verify(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.codes_file_path = 'settings/userdata/keys.json'
        self.users_file_path = 'settings/userdata/users.json'
        self.embed_config_path = 'settings/verify.json'

        # Create files if they don't exist
        if not os.path.exists(self.codes_file_path):
            with open(self.codes_file_path, 'w') as file:
                json.dump({}, file)
        
        if not os.path.exists(self.users_file_path):
            with open(self.users_file_path, 'w') as file:
                json.dump({}, file)
        
        # Load embed configuration
        with open(self.embed_config_path, 'r') as file:
            self.embed_config = json.load(file)['embed']

    @commands.slash_command(name="verify", description="bloxlose.com/verify.html")
    async def verify(self, inter: disnake.ApplicationCommandInteraction, code: str):
        user_id = str(inter.user.id)
        
        # Load the verification codes
        with open(self.codes_file_path, 'r') as file:
            verification_codes = json.load(file)
        
        # Check if the code is valid
        if user_id in verification_codes and verification_codes[user_id] == code:
            # Mark the user as verified
            with open(self.users_file_path, 'r') as file:
                users = json.load(file)
                
            users[user_id] = {"verified": True}
            
            with open(self.users_file_path, 'w') as file:
                json.dump(users, file)
            
            # Remove the used code
            del verification_codes[user_id]
            
            with open(self.codes_file_path, 'w') as file:
                json.dump(verification_codes, file)
            
            await inter.response.send_message("Your account has been verified!", ephemeral=True)
        else:
            await inter.response.send_message("Invalid code or code has expired. Make sure you use /getcode first.", ephemeral=True)

    @commands.slash_command(name="getcode", description="Get a verification code.")
    async def getcode(self, inter: disnake.ApplicationCommandInteraction):
        user_id = str(inter.user.id)
        
        # Check if user is already verified
        with open(self.users_file_path, 'r') as file:
            users = json.load(file)
        
        if user_id in users and users[user_id].get('verified', False):
            await inter.response.send_message("You are already verified.", ephemeral=True)
            return
        
        # Generate the obfuscated code
        obfuscated_code = self.generate_obfuscated_code(user_id)
        
        # Save the obfuscated code
        with open(self.codes_file_path, 'r') as file:
            verification_codes = json.load(file)
        
        verification_codes[user_id] = obfuscated_code
        
        with open(self.codes_file_path, 'w') as file:
            json.dump(verification_codes, file)
        
        # Create the embed using the configuration
        embed_config = self.embed_config
        
        embed = disnake.Embed(
            title=embed_config['title'],
            description=embed_config['description'].replace('CODE', user_id),
            color=embed_config['color']
        )
        embed.set_footer(
            text=embed_config['footer']['text'],
            icon_url=embed_config['footer']['icon_url']
        )
        
        await inter.response.send_message(embed=embed, ephemeral=True)

    def generate_obfuscated_code(self, user_id):
        # Simple obfuscation example: mapping digits to characters
        digit_to_char = {
            '0': 'A', '1': 'O', '2': 'G', '3': 'H',
            '4': 'X', '5': 'R', '6': '8', '7': '4',
            '8': '6', '9': '0'
        }
        
        # Generate obfuscated code using the mapping
        return ''.join(digit_to_char.get(digit, '?') for digit in user_id)

def setup(bot):
    bot.add_cog(Verify(bot))
    print(f'{Colors.WHITE} +{Colors.GREEN} verify.py{Colors.RESET}')
