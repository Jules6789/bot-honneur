import discord
from discord.ext import commands
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os

# ---------------------- CONFIGURATION ----------------------
TOKEN = os.getenv("TOKEN")  # À configurer dans Render comme variable d'environnement
GUILD_ID = None  # Laisser None sauf si tu veux restreindre le bot à un serveur
SPREADSHEET_NAME = "bot-honneur"  # À adapter selon le nom exact de ton Google Sheet
SHEET_NAME = "Feuille 1"  # À adapter si besoin

# ---------------------- GOOGLE SHEETS SETUP ----------------------
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("service-account.json", scope)
client = gspread.authorize(creds)
sheet = client.open(SPREADSHEET_NAME).worksheet(SHEET_NAME)

# ---------------------- DISCORD SETUP ----------------------
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

# ---------------------- FONCTION UTILE ----------------------
def update_points(user_id, amount):
    users = sheet.col_values(1)
    if user_id in users:
        cell = sheet.find(user_id)
        old_score = int(sheet.cell(cell.row, 2).value)
        sheet.update_cell(cell.row, 2, old_score + amount)
    else:
        sheet.append_row([user_id, amount])

# ---------------------- COMMANDES DISCORD ----------------------
@bot.command()
async def honor(ctx, member: discord.Member):
    update_points(str(member.id), 1)
    await ctx.send(f"✅ {member.mention} a bien reçu un diamant 💎 d'honneur !")

@bot.command()
async def top(ctx):
    users = sheet.get_all_values()[1:]  # Ignore header
    sorted_users = sorted(users, key=lambda x: int(x[1]), reverse=True)
    message = "**Classement d'honneur :**\n"
    for i, (user_id, score) in enumerate(sorted_users[:10], 1):
        user = await bot.fetch_user(int(user_id))
        message += f"{i}. {user.name} : {score} 💎\n"
    await ctx.send(message)

# ---------------------- DÉMARRAGE ----------------------
bot.run(TOKEN)
