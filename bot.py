
import discord
from discord.ext import commands
import aiosqlite
from config import TOKEN
from rank_card import generate_rank_card
from flask import Flask



app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)





intents = discord.Intents.default()
intents.message_content = True
intents.members = True



bot = commands.Bot(command_prefix="!", intents=intents)

LEVEL_ROLES = {
    10: 1375718667488333855,    # Bronze
    25: 1375718907666628639,    # Silver
    50: 1375719008325603379,    # Gold
    100: 1375719138747617350,   # Diamond
    200: 1375719259560480889    # Legend
}

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    async with aiosqlite.connect("level.db") as db:
        await db.execute("CREATE TABLE IF NOT EXISTS levels (user_id INTEGER PRIMARY KEY, xp INTEGER, level INTEGER)")
        await db.commit()

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    user_id = message.author.id
    async with aiosqlite.connect("level.db") as db:
        async with db.execute("SELECT xp, level FROM levels WHERE user_id = ?", (user_id,)) as cursor:
            row = await cursor.fetchone()
        if row:
            xp, level = row
        else:
            xp, level = 0, 1

        xp += 10
        next_level_xp = level * 100
        leveled_up = False

        if xp >= next_level_xp:
            level += 1
            xp -= next_level_xp
            leveled_up = True

        await db.execute("REPLACE INTO levels (user_id, xp, level) VALUES (?, ?, ?)", (user_id, xp, level))
        await db.commit()

    if leveled_up:
        member = message.guild.get_member(user_id)
        current_roles = [r.id for r in member.roles]
        for role_id in LEVEL_ROLES.values():
            if role_id in current_roles:
                await member.remove_roles(discord.Object(id=role_id))

        new_role_id = LEVEL_ROLES.get(level)
        if new_role_id:
            await member.add_roles(discord.Object(id=new_role_id))

        await message.channel.send(f"🎉 {message.author.mention} leveled up to **Level {level}**!")

    await bot.process_commands(message)

@bot.command()
async def rank(ctx):
    user_id = ctx.author.id
    async with aiosqlite.connect("level.db") as db:
        async with db.execute("SELECT xp, level FROM levels WHERE user_id = ?", (user_id,)) as cursor:
            row = await cursor.fetchone()
    if row:
        xp, level = row
        image = await generate_rank_card(ctx.author, xp, level)
        await ctx.send(file=discord.File(fp=image, filename="rank.png"))
    else:
        await ctx.send("You don't have any XP yet. Start chatting!")

bot.run(TOKEN)
