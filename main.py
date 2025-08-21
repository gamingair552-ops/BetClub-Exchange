import discord
from discord.ext import commands
from discord.ui import View, Button
import qrcode, io, os

bot = commands.Bot(command_prefix=".", intents=discord.Intents.all())

INR_TO_USDT_RATE = 93  # Fixed INR → USDT conversion for .i2c

# ---------- INR to Crypto ----------
@bot.command()
async def i2c(ctx, member: discord.Member, upi: str, amount: float):
    """
    Usage: .i2c @user upi_id amount
    Example: .i2c @rjhemant pushpa1811@ptaxis 500
    """
    usdt = round(amount / INR_TO_USDT_RATE, 2)
    
    # Generate UPI QR
    buffer = io.BytesIO()
    qrcode.make(f"upi://pay?pa={upi}&am={amount}&cu=INR").save(buffer, format="PNG")
    buffer.seek(0)
    
    vouch_text = f"+rep {member.mention} Legit Exchange • {amount} INR"
    
    embed = discord.Embed(
        title="✅ Payment & Vouch (INR → Crypto)",
        description=f"**UPI:** `{upi}`\n**Amount:** ₹{amount} (~{usdt} USDT)\n"
                    f"💎 {ctx.author.mention} vouched for {member.mention}\n\n"
                    f"Click the button below to copy the vouch text!",
        color=0x2ecc71
    )
    embed.set_image(url="attachment://upi_qr.png")
    
    class CopyButtonView(View):
        @discord.ui.button(label="Copy Vouch", style=discord.ButtonStyle.green)
        async def copy_button(self, interaction: discord.Interaction, button: discord.ui.Button):
            await interaction.response.send_message(f"Copied to clipboard:\n```{vouch_text}```", ephemeral=True)
    
    await ctx.send(embed=embed, file=discord.File(buffer, "upi_qr.png"), view=CopyButtonView())


# ---------- Crypto to INR ----------
@bot.command()
async def c2i(ctx, member: discord.Member, crypto_address: str, amount: float):
    """
    Usage: .c2i @user crypto_address amount_in_usd
    Example: .c2i @rjhemant 0x123abc456def 45
    """
    # Tiered INR conversion rate based on amount
    if amount < 50:
        rate = 88
    elif 50 <= amount <= 99:
        rate = 88.5
    else:  # amount > 99
        rate = 88

    inr = round(amount * rate, 2)
    
    # Generate QR for crypto address
    buffer = io.BytesIO()
    qrcode.make(f"{crypto_address}").save(buffer, format="PNG")
    buffer.seek(0)
    
    vouch_text = f"+rep {member.mention} Legit Exchange • {amount} Crypto (~₹{inr})"
    
    embed = discord.Embed(
        title="✅ Payment & Vouch (Crypto → INR)",
        description=f"**Crypto Address:** `{crypto_address}`\n**Amount:** {amount} Crypto (~₹{inr})\n"
                    f"💎 {ctx.author.mention} vouched for {member.mention}\n\n"
                    f"Click the button below to copy the vouch text!",
        color=0x3498db
    )
    embed.set_image(url="attachment://crypto_qr.png")
    
    class CopyButtonView(View):
        @discord.ui.button(label="Copy Vouch", style=discord.ButtonStyle.green)
        async def copy_button(self, interaction: discord.Interaction, button: discord.ui.Button):
            await interaction.response.send_message(f"Copied to clipboard:\n```{vouch_text}```", ephemeral=True)
    
    await ctx.send(embed=embed, file=discord.File(buffer, "crypto_qr.png"), view=CopyButtonView())


bot.run("DISCORD_BOT_TOKEN")
