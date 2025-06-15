import discord
from discord.ext import commands
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import json

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="/", intents=intents)

# Lecture du JSON depuis la variable d'environnement
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds_dict = json.loads(os.getenv("GOOGLE_CREDS"))
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)

# Connexion à la feuille Google Sheets
sheet = client.open_by_key(os.getenv("SHEET_ID")).sheet1

@bot.event
async def on_ready():
    print(f"{bot.user} est en ligne ✅")

@bot.command()
async def add(ctx, member: discord.Member, points: int):
    ids = sheet.col_values(1)
    uid = str(member.id)
    if uid in ids:
        i = ids.index(uid) + 1
        current = int(sheet.cell(i, 3).value)
        sheet.update_cell(i, 3, current + points)
    else:
        sheet.append_row([uid, member.name, points])
    await ctx.send(f"💎 {points} points ajoutés à {member.display_name}")

@bot.command()
async def remove(ctx, member: discord.Member, points: int):
    ids = sheet.col_values(1)
    uid = str(member.id)
    if uid in ids:
        i = ids.index(uid) + 1
        current = int(sheet.cell(i, 3).value)
        sheet.update_cell(i, 3, max(0, current - points))
        await ctx.send(f"💎 {points} points retirés à {member.display_name}")
    else:
        await ctx.send(f"{member.display_name} n’a pas de points")

bot.run(os.getenv("TOKEN"))


