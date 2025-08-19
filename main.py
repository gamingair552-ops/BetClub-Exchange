import discord
from discord.ext import commands
from discord import app_commands
from flask import Flask
from threading import Thread
import qrcode
from io import BytesIO

# Bot prefix and name
BOT_PREFIX = "+"
BOT_NAME = "BETCLUB EXCHANGE"

# Exchange rates (can be edited only by owner)
INR_TO_CRYPTO_RATE = 92  # INR -> USD (crypto)
c2i_rates = {'below_50': 88, '50_to_100': 88.5, 'above_100': 89}

# Dictionary to store vouches
vouches = {}

# Dictionary to store user addresses or custom responses
autoresponses = {}

# Flask keep-alive server
app = Flask('')

@app.route('/')
def home():
    return "BETCLUB EXCHANGE is running!"

def run():
    app.run(host='0.0.0.0', port=8000)

def keep_alive():
    t = Thread(target=run)
    t.start()

# IDs
OWNER_ID = 1288745766340263954  # Replace with @rjhemant Discord ID

# Check if the user is an administrator
def is_admin(ctx):
    return ctx.author.guild_permissions.administrator

# Check if the user is the owner
def is_owner(ctx):
    return ctx.author.id == OWNER_ID

# Create bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=BOT_PREFIX, intents=intents, help_command=None)
sync_tree = bot.tree

@bot.event
async def on_ready():
    await sync_tree.sync()  # Sync slash commands
    print(f"{BOT_NAME} is online!")

# Function to get c2i rate based on amount
def get_rate(amount: float) -> float:
    if amount < 50:
        return c2i_rates['below_50']
    elif 50 <= amount <= 100:
        return c2i_rates['50_to_100']
    else:
        return c2i_rates['above_100']

# Owner-only command to change rates
@bot.command()
@commands.check(is_owner)
async def setrate(ctx, tier: str, rate: float):
    if tier.lower() == 'inr_to_crypto':
        global INR_TO_CRYPTO_RATE
        INR_TO_CRYPTO_RATE = rate
        await ctx.send(f"✅ INR to Crypto rate updated to {rate}")
    elif tier.lower() in ['below_50','50_to_100','above_100']:
        c2i_rates[tier.lower()] = rate
        await ctx.send(f"✅ {tier} C2I rate updated to {rate}")
    else:
        await ctx.send("❌ Invalid tier. Use 'inr_to_crypto', 'below_50', '50_to_100', 'above_100'")

# INR to Crypto command (admins only)
@bot.command()
@commands.check(is_admin)
async def i2c(ctx, amount: float):
    crypto_value = amount / INR_TO_CRYPTO_RATE
    await ctx.send(f"💱 {amount:.2f} INR = **{crypto_value:.4f}$** (Crypto)")

# Crypto to INR command (admins only)
@bot.command()
@commands.check(is_admin)
async def c2i(ctx, amount: str):
    try:
        if amount.endswith("$"):
            amount = amount[:-1]
        crypto_amount = float(amount)

        rate = get_rate(crypto_amount)
        inr_value = crypto_amount * rate
        await ctx.send(f"💱 {crypto_amount:.4f}$ = **{inr_value:.2f} INR**")
    except ValueError:
        await ctx.send("❌ Invalid amount. Example: +c2i 50 or +c2i 50$")

# Vouch system (everyone can use)
@bot.command()
async def vouch(ctx, member: discord.Member):
    user_id = member.id
    vouches[user_id] = vouches.get(user_id, 0) + 1
    await ctx.send(f"✅ {member.mention} has been vouched! Total vouches: {vouches[user_id]}")

# Check vouches (admins only)
@bot.command()
@commands.check(is_admin)
async def checkvouch(ctx, member: discord.Member):
    user_id = member.id
    total = vouches.get(user_id, 0)
    await ctx.send(f"📄 {member.mention} has **{total}** vouches")

# Autoresponder (admins only)
@bot.command()
@commands.check(is_admin)
async def addy(ctx, *, message: str = None):
    user_id = ctx.author.id
    if message:
        autoresponses[user_id] = message
        await ctx.send(f"✅ Your saved message has been set!")
    else:
        saved_message = autoresponses.get(user_id)
        if saved_message:
            await ctx.send(saved_message)  # Only show saved message without extra text
        else:
            await ctx.send("❌ You have not set any message yet. Use `+addy <your message>` to set it.")

# QR code generation command (admins only)
@bot.command()
@commands.check(is_admin)
async def makeqr(ctx, upi_id: str, amount: float):
    qr_text = f"upi://pay?pa={upi_id}&am={amount}&cu=INR"
    qr_img = qrcode.make(qr_text)
    buffer = BytesIO()
    qr_img.save(buffer, format="PNG")
    buffer.seek(0)
    file = discord.File(fp=buffer, filename="upi_qr.png")
    await ctx.send(f"✅ QR code generated for {upi_id} ({amount} INR)", file=file)

# Custom help command
@bot.command()
async def help(ctx):
    help_text = (
        f"**{BOT_NAME} Commands (Vouch = Everyone, Admins Only for Others, Owner Manages Rates)**\n"
        "```"
        "+i2c <INR>   → Convert INR to Crypto (admins only)"
        "+c2i <USD>$  → Convert Crypto to INR (admins only)"
        "+c2i <USD>   → Auto-detect rate without $ (admins only)"
        "+vouch <@user> → Give a vouch to a user (everyone"
        "+checkvouch <@user> → Check vouches of a user (admins only)"
        "+addy [message] → Save or show your message (admins only)"
        "+makeqr <upi_id> <amount> → Generate UPI QR code (admins only)"
        "+setrate <tier> <rate> → Owner only, change bot rates"
        "Rates: <50$ = 88 | 50-100$ = 88.5 | >100$ = 89"
        "```"
    )
    await ctx.send(help_text)

# Start keep-alive server
keep_alive()

# Run bot (replace with your token)
TOKEN = "MTQwNjE2NjMwMTg1MjA0NTMxMg.GrEH2z.PL1tBiu94l_S7g7BDwtHooeqRcQXsEyVhhnYXQ"
bot.run(TOKEN)



