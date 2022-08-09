import os
import asyncio
from datetime import timedelta
import datetime
from datetime import *
import discord
from discord import Option
from discord.ext import commands
from discord.ext.commands import *
from discord.ui import *
import aiohttp
import random
import pymongo
import certifi
from pymongo import MongoClient

e = certifi.where()
intents = discord.Intents().all()
token = os.environ['TOKEN'] 
mango_url = os.environ['MONGO'] 
cluster = MongoClient(mango_url, tlsCAFile=e)
db = cluster["skytrek"]
coll = db["prefix"]

def prefix(client, message):
    prefix = coll.find_one({"_id": message.guild.id})["prefix"]
    return prefix

client = commands.Bot(command_prefix=prefix,
                      case_insensitive=True,intents=intents)

client.launch_time = datetime.utcnow()

@client.event
async def on_ready():
    await client.change_presence(status=discord.Status.dnd, activity=discord.Game(name=f"on {len(client.guilds)} servers"))
    await client.change_presence(status=discord.Status.dnd, activity=discord.Activity(type=discord.ActivityType.watching, name="sk!help"))
    await client.change_presence(status=discord.Status.dnd, activity=discord.Activity(type=discord.ActivityType.listening, name="Slash Commands!"))
    print(f"{client.user.name} is ready")


async def status():
    await client.wait_until_ready()

    statuses = [f"on {len(client.guilds)} servers", "sk!help"]

    while not client.is_closed():

        status = random.choice(statuses)
        await client.change_presence(status=discord.Status.dnd, activity=discord.Game(name=status))

        await asyncio.sleep(10)

@client.event
async def on_guild_join(guild):
    coll.insert_one({"_id": guild.id, "prefix": "cb!"})


@client.event
async def on_guild_remove(guild):
    coll.delete_one({"_id": guild.id})


@client.command(aliases=['prefix'])
@commands.has_permissions(manage_guild=True)
@commands.cooldown(1, 5, commands.BucketType.user)
async def setprefix(ctx, prefix=None):
    if prefix is None:
        await ctx.reply("Please enter a prefix!", delete_after=5)
    else:
        coll.update_one({"_id": ctx.guild.id}, {
                        "$set": {"prefix": prefix}}, upsert=True)
        await ctx.reply("**Prefix has been changed to:** `{}`".format(prefix))


client.loop.create_task(status())
client.run(token)
