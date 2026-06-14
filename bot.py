import discord
from discord.ext import commands
import json
import time
from datetime import datetime
import os

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

DATA_FILE = "duty.json"

panel_message = None

def load_data():
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

data = load_data()


# 📊 PANEL UPDATE
async def update_panel(channel):

    embed = discord.Embed(
        title="📋 DUTY PANEL",
        description="Klikni dugmad ispod za Start / Stop duty",
        color=0x00ff00
    )

    active_users = []
    for uid, info in data.items():
        if info.get("active"):
            active_users.append(f"<@{uid}> 🟢 ON DUTY")

    if active_users:
        embed.add_field(name="🟢 Trenutno na duty:", value="\n".join(active_users), inline=False)
    else:
        embed.add_field(name="🟢 Trenutno na duty:", value="Niko nije na duty-u", inline=False)

    global panel_message

    if panel_message:
        await panel_message.edit(embed=embed, view=DutyView())


# 🎮 BUTTONS
class DutyView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Start Duty 🟢", style=discord.ButtonStyle.success)
    async def start(self, interaction: discord.Interaction, button: discord.ui.Button):

        user = str(interaction.user.id)

        if user in data and data[user].get("active"):
            await interaction.response.send_message("❌ Već si na duty-u!", ephemeral=True)
            return

        data[user] = data.get(user, {})
        data[user]["active"] = True
        data[user]["start_time"] = time.time()
        data[user]["total"] = data[user].get("total", 0)

        save_data(data)

        await interaction.response.send_message("🟢 Duty START", ephemeral=True)

        await update_panel(interaction.channel)


    @discord.ui.button(label="Stop Duty 🔴", style=discord.ButtonStyle.danger)
    async def stop(self, interaction: discord.Interaction, button: discord.ui.Button):

        user = str(interaction.user.id)

        if user not in data or not data[user].get("active"):
            await interaction.response.send_message("❌ Nisi na duty-u!", ephemeral=True)
            return

        start_time = data[user]["start_time"]
        duration = time.time() - start_time

        data[user]["active"] = False
        data[user]["total"] = data[user].get("total", 0) + duration

        save_data(data)

        hours = round(duration / 3600, 2)
        total_hours = round(data[user]["total"] / 3600, 2)

        await interaction.response.send_message(
            f"🔴 Duty STOP\n⏱ Radio: {hours}h\n📊 Ukupno: {total_hours}h",
            ephemeral=True
        )

        await update_panel(interaction.channel)


# 📋 PANEL KOMANDA
@bot.command()
async def panel(ctx):

    global panel_message

    embed = discord.Embed(
        title="📋 DUTY PANEL",
        description="Klikni dugmad ispod za Start / Stop duty",
        color=0x00ff00
    )

    panel_message = await ctx.send(embed=embed, view=DutyView())


# 🔵 BOT READY
@bot.event
async def on_ready():
    print(f"Bot je online kao {bot.user}")


# 🚀 RUN BOT
bot.run(os.getenv("DISCORD_TOKEN"))