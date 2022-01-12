import asyncio
import os
import random
import sys

import aiohttp
import aiofiles
import hashlib
import discord
import yaml
from discord.ext import commands
from discord.ext.commands import BucketType
import requests
import uuid
import inspirobot
import uwuify
import language_tool_python
import contractions
import torch
from transformers import GPT2LMHeadModel, GPT2Tokenizer

if not os.path.isfile("config.yaml"):
    sys.exit("'config.yaml' not found! Please add it and try again.")
else:
    with open("config.yaml") as file:
        config = yaml.load(file, Loader=yaml.FullLoader)


class Fun(commands.Cog, name="fun"):
    def __init__(self, bot):
        self.languageTool = language_tool_python.LanguageTool('en-US')
        self.tokenizer = GPT2Tokenizer.from_pretrained('gpt2')
        self.model = GPT2LMHeadModel.from_pretrained('gpt2')
        self.bot = bot

    @commands.command(name="gpt")
    async def gpt(self, context, *args):
        """
        Dad is creative.
        """
        inputs = self.tokenizer.encode(" ".join(args), return_tensors='pt')
        outputs = self.model.generate(inputs, max_length=200, do_sample=True)
        text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        await context.reply(text)

    @commands.command(name="randomfact")
    async def randomfact(self, context):
        """
        Dad has learned a few things, he'll share.
        """
        # This will prevent your bot from stopping everything when doing a web request - see: https://discordpy.readthedocs.io/en/stable/faq.html#how-do-i-make-a-web-request
        async with aiohttp.ClientSession() as session:
            async with session.get("https://uselessfacts.jsph.pl/random.json?language=en") as request:
                if request.status == 200:
                    data = await request.json()
                    embed = discord.Embed(description=data["text"], color=config["main_color"])
                    await context.send(embed=embed)
                else:
                    embed = discord.Embed(
                        title="Error!",
                        description="There is something wrong with the API, please try again later",
                        color=config["error"]
                    )
                    await context.reply(embed=embed)

    @commands.command(name="dadjoke")
    async def dadjoke(self, context, searchTerm="", *args):
        """
        Have Dad tell you one of his classics.
        """
        url = "https://icanhazdadjoke.com/search?term=" + searchTerm
        headers = {'Accept': 'application/json'}
        r = requests.get(url, headers=headers)
        json = r.json()
        try:
            await context.reply(random.choice(json["results"])["joke"])
        except:
            await context.reply("I don't think I've heard a good one about that yet. Try something else.")
    
    @commands.command(name="inspire")
    async def inspire(self, context):
        """
        Get an inspirational poster courtesy of https://inspirobot.me/
        """
        quote = inspirobot.generate()
        await context.reply(quote.url)
    
    @commands.command(name="wisdom")
    async def wisdom(self, context):
        """
        Get some wisdom courtesy of https://inspirobot.me/
        """
        flow = inspirobot.flow()  # Generate a flow object
        res = ""
        for quote in flow:
            res += quote.text + "\n"
        
        await context.reply(res)

    @commands.command(name="advice")
    async def advice(self, context):
        """
        Get some fatherly advice.
        """
        r = requests.get("https://api.adviceslip.com/advice")
        await context.reply(r.json()['slip']['advice'])
    
    @commands.command(name="xkcd")
    async def xkcd(self, context, search=""):
        """
        Retrieve a random or specific xkcd comic, specify a number like "!xkcd 1" to get the first xkcd comic.
        """
        r = requests.get("http://xkcd.com/info.0.json")
        search = search if search != "" else str(random.choice(range(1, r.json()['num'])))

        r = requests.get("http://xkcd.com/" + search + "/info.0.json")

        try:
            await context.reply(r.json()['img'])
        except:
            await context.reply("I can't find that xkcd comic, try another.")
    
    @commands.command(name="iswanted")
    async def iswanted(self, context, *args):
        """
        See if someone is on the FBI's most wanted list.
        """
        name = " ".join(args).strip()
        r = requests.get("https://api.fbi.gov/wanted/v1/list", params={"title": name})

        try:
            url = random.choice(r.json()['items'])["files"][0]['url']
            await context.reply(name + " might be wanted by the FBI:\n" + url)
        except:
            await context.reply("No one with that name is currently wanted by the FBI")
    
    @commands.command(name="roastme")
    async def roastme(self, context):
        """
        Dad's been around the block a few times, give him a try.
        """

        url = "https://evilinsult.com/generate_insult.php?lang=en&type=json"
        r = requests.get(url)
        json = r.json()
        await context.reply(json["insult"])

    @commands.command(name="rps")
    async def rock_paper_scissors(self, context):
        """
        Play a round of Rock-Paper-Scissors with Dad.
        """
        choices = {
            0: "rock",
            1: "paper",
            2: "scissors"
        }
        reactions = {
            "🪨": 0,
            "🧻": 1,
            "✂": 2
        }
        embed = discord.Embed(title="Please choose", color=config["warning"])
        embed.set_author(name=context.author.display_name, icon_url=context.author.avatar_url)
        choose_message = await context.send(embed=embed)
        for emoji in reactions:
            await choose_message.add_reaction(emoji)

        def check(reaction, user):
            return user == context.message.author and str(reaction) in reactions

        try:
            reaction, user = await self.bot.wait_for("reaction_add", timeout=10, check=check)

            user_choice_emote = reaction.emoji
            user_choice_index = reactions[user_choice_emote]

            bot_choice_emote = random.choice(list(reactions.keys()))
            bot_choice_index = reactions[bot_choice_emote]

            result_embed = discord.Embed(color=config["success"])
            result_embed.set_author(name=context.author.display_name, icon_url=context.author.avatar_url)
            await choose_message.clear_reactions()

            if user_choice_index == bot_choice_index:
                result_embed.description = f"**That's a draw!**\nYou've chosen {user_choice_emote} and I've chosen {bot_choice_emote}."
                result_embed.colour = config["warning"]
            elif user_choice_index == 0 and bot_choice_index == 2:
                result_embed.description = f"**You won!**\nYou've chosen {user_choice_emote} and I've chosen {bot_choice_emote}."
                result_embed.colour = config["success"]
            elif user_choice_index == 1 and bot_choice_index == 0:
                result_embed.description = f"**You won!**\nYou've chosen {user_choice_emote} and I've chosen {bot_choice_emote}."
                result_embed.colour = config["success"]
            elif user_choice_index == 2 and bot_choice_index == 1:
                result_embed.description = f"**You won!**\nYou've chosen {user_choice_emote} and I've chosen {bot_choice_emote}."
                result_embed.colour = config["success"]
            else:
                result_embed.description = f"**I won!**\nYou've chosen {user_choice_emote} and I've chosen {bot_choice_emote}."
                result_embed.colour = config["error"]
                await choose_message.add_reaction("🇱")
            await choose_message.edit(embed=result_embed)
        except asyncio.exceptions.TimeoutError:
            await choose_message.clear_reactions()
            timeout_embed = discord.Embed(title="Too late", color=config["error"])
            timeout_embed.set_author(name=context.author.display_name, icon_url=context.author.avatar_url)
            await choose_message.edit(embed=timeout_embed)
    
    @commands.command(name="newperson")
    async def newperson(self, context):
        """
        Creates a picture of a person that does not exist.(From https://thispersondoesnotexist.com/)
        """
        fileName = str(uuid.uuid1()) + str(random.choice(range(1, 1337))) + ".png"
        await self.save_online_person(fileName)
        file = discord.File(fileName, filename="newperson.png")
        await context.send("", file=file)
        os.remove(fileName)
    
    @commands.command(name="uwu")
    async def uwu(self, context):
        """
        UwU
        """
        message = await context.channel.fetch_message(context.message.reference.message_id)
        flags = uwuify.SMILEY | uwuify.YU
        await context.reply(uwuify.uwu(message.content, flags=flags))
    
    @commands.command(name="antiuwu")
    async def antiuwu(self, context):
        """
        UwU but scholarly
        """
        message = await context.channel.fetch_message(context.message.reference.message_id)
        text = message.content
        corrected = contractions.fix(self.languageTool.correct(text))
        await context.reply(corrected)

    @commands.command(name="blockeningSupport")
    async def blockeningSupport(self, context):
        """
        For support
        """
        channel = context.author.voice.channel
        await context.reply("On my way!")
        await channel.connect()
    
    @commands.command(name="drawerpc")
    async def newperson(self, context):
        """
        Replies with "DRAWER PC DRAWER PC"
        """
        await context.send("DRAWER PC DRAWER PC")
        
    @commands.command(name="newcat")
    async def newcat(self, context):
        """
        Creates a picture of a cat that does not exist. (From https://thiscatdoesnotexist.com/)
        """
        fileName = str(uuid.uuid1()) + str(random.choice(range(1, 1337))) + ".png"
        await self.save_online_cat(fileName)
        file = discord.File(fileName, filename="newcat.png")
        await context.send("", file=file)
        os.remove(fileName)

    async def get_online_person(self) -> bytes:
        url = "https://thispersondoesnotexist.com/image"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36'
        }
        async with aiohttp.ClientSession() as s:
            async with s.get(url, headers=headers) as r:
                return await r.read()

    async def save_online_person(self, file: str = None) -> int:
        picture = await self.get_online_person()
        return await self.save_picture(picture, file)
    
    async def get_online_cat(self) -> bytes:
        url = "https://thiscatdoesnotexist.com"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36'
        }
        async with aiohttp.ClientSession() as s:
            async with s.get(url, headers=headers) as r:
                return await r.read()

    async def save_online_cat(self, file: str = None) -> int:
        picture = await self.get_online_cat()
        return await self.save_picture(picture, file)
    
    async def get_checksum_from_picture(self, picture: bytes, method: str = "md5") -> str:
        """Calculate the checksum of the provided picture, using the desired method.
        Available methods can be fetched using the the algorithms_available function.
        :param picture: picture as bytes
        :param method: hashing method as string (optional, default=md5)
        :return: checksum as string
        """
        h = hashlib.new(method.lower())
        h.update(picture)
        return h.hexdigest()
    
    async def save_picture(self, picture: bytes, file: str = None) -> None:
        """Save a picture to a file.
        The picture must be provided as it content as bytes.
        The filename must be provided as a str with the absolute or relative path where to store it.
        If no filename is provided, a filename will be generated using the MD5 checksum of the picture, with jpeg extension.
        :param picture: picture content as bytes
        :param file: filename as string, relative or absolute path (optional)
        :return: None
        """
        if file is None:
            file = self.get_checksum_from_picture(picture) + ".jpeg"
        async with aiofiles.open(file, "wb") as f:
            await f.write(picture)

def setup(bot):
    bot.add_cog(Fun(bot))
