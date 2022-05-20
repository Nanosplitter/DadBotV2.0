import json
import os
import platform
import random
import sys
import mysql.connector
import dateparser as dp
import pytz
import datetime
from dateparser.search import search_dates
from colour import Color

import aiohttp
import nextcord
import requests
import yaml
from nextcord.ext import commands
from nextcord.ext import tasks
from noncommands import summarizer
from noncommands import birthdayLoop
if "DadBot" not in str(os.getcwd()):
    os.chdir("./DadBot")
with open("config.yaml") as file:
    config = yaml.load(file, Loader=yaml.FullLoader)


class general(commands.Cog, name="general"):
    def __init__(self, bot):
        self.bot = bot
        self.birthdayLoop = birthdayLoop.BirthdayLoop(bot)

    @commands.command(name="info", aliases=["botinfo"])
    async def info(self, context):
        """
        Get some useful (or not) information about the bot.
        """
        embed = nextcord.Embed(
            description="The server's dad",
            color=config["success"]
        )
        embed.set_author(
            name="Bot Information"
        )
        embed.add_field(
            name="Owner:",
            value="Nanosplitter#4549",
            inline=True
        )
        embed.add_field(
            name="Python Version:",
            value=f"{platform.python_version()}",
            inline=True
        )
        embed.add_field(
            name="Prefix:",
            value=f"{config['bot_prefix']}",
            inline=False
        )
        embed.set_footer(
            text=f"Requested by {context.message.author}"
        )
        await context.send(embed=embed)

    @commands.command(name="serverinfo")
    async def serverinfo(self, context):
        """
        Get some useful (or not) information about the server.
        """
        server = context.message.guild
        roles = [x.name for x in server.roles]
        role_length = len(roles)
        if role_length > 50:
            roles = roles[:50]
            roles.append(f">>>> Displaying[50/{len(roles)}] Roles")
        roles = ", ".join(roles)
        channels = len(server.channels)
        time = str(server.created_at)
        time = time.split(" ")
        time = time[0]

        embed = nextcord.Embed(
            title="**Server Name:**",
            description=f"{server}",
            color=config["success"]
        )
        embed.set_thumbnail(
            url=server.icon_url
        )
        embed.add_field(
            name="Server ID",
            value=server.id
        )
        embed.add_field(
            name="Member Count",
            value=server.member_count
        )
        embed.add_field(
            name="Text/Voice Channels",
            value=f"{channels}"
        )
        embed.add_field(
            name=f"Roles ({role_length})",
            value=roles
        )
        embed.set_footer(
            text=f"Created at: {time}"
        )
        await context.send(embed=embed)
    
    @commands.command(name="setbirthday")
    async def setbirthday(self, context, *birthday):
        """
        Dad always remembers birthdays.
        """
        mydb = mysql.connector.connect(
            host=config["dbhost"],
            user=config["dbuser"],
            password=config["dbpassword"],
            database=config["databasename"],
            autocommit=True
        )
        timeStr = " ".join(birthday).lower()
        time = dp.parse(timeStr, settings={'TIMEZONE': 'US/Eastern', 'RETURN_AS_TIMEZONE_AWARE': True, 'PREFER_DATES_FROM': 'future', 'PREFER_DAY_OF_MONTH': 'first'})
        timeWords = timeStr
        f = '%Y-%m-%d %H:%M:%S'
        if time is None:
            searchRes = search_dates(timeStr, settings={'TIMEZONE': 'US/Eastern', 'RETURN_AS_TIMEZONE_AWARE': True, 'PREFER_DATES_FROM': 'future', 'PREFER_DAY_OF_MONTH': 'first'}, languages=['en'])
            for t in searchRes:
                time = t[1]
                timeWords = t[0]
                break
            
        if time is not None:
            timeUTC = dp.parse(time.strftime(f), settings={'TIMEZONE': 'US/Eastern', 'TO_TIMEZONE': 'UTC'})
            mycursor = mydb.cursor(buffered=True)
            mycursor.execute(f"DELETE FROM birthdays WHERE author = '{context.message.author}'")
            mydb.commit()
            mycursor.execute("INSERT INTO birthdays (author, mention, channel_id, birthday) VALUES ('"+ str(context.message.author) +"', '"+ str(context.message.author.mention) +"', '"+ str(context.channel.id) +"', '"+ timeUTC.strftime(f) +"')")
            print(time)
            await context.reply("Your Birthday is set for: " + time.strftime(f) + " EST \n\nHere's the time I read: " + timeWords)
            mydb.commit()
            mycursor.close()
            mydb.close()
        else:
            await context.reply("I can't understand that time, try again but differently")
    
    @commands.command(name="todaysbirthdays")
    async def todaysbirthdays(self, context):
        await self.birthdayLoop.checkBirthdays()

    @commands.command(name="nobitches")
    async def nobitches(self, context, *text):
        params = {
            "template_id": "370867422", 
            "username": "nanosplitter", 
            "password": config["imgflip_pass"],
            "text0": " ".join(text),
        }
        r = requests.post("https://api.imgflip.com/caption_image", params=params)
        await context.send(r.json()["data"]["url"])

    @commands.command(name="ping")
    async def ping(self, context):
        """
        Check if the bot is alive.
        """
        embed = nextcord.Embed(
            color=config["success"]
        )
        embed.add_field(
            name="Pong!",
            value=":ping_pong:",
            inline=True
        )
        embed.set_footer(
            text=f"Pong request by {context.message.author}"
        )
        await context.send(embed=embed)
    
    def luminance(self, color):
        """
        Calculate the luminance of a color.
        """
        red = Color(color).red
        green = Color(color).green
        blue = Color(color).blue

        red = red / 12.92 if red <= 0.04045 else ((red + 0.055) / 1.055)**2.4
        green = green / 12.92 if green <= 0.04045 else ((green + 0.055) / 1.055)**2.4
        blue = blue / 12.92 if blue <= 0.04045 else ((blue + 0.055) / 1.055)**2.4

        print(color, red, green, blue)

        return (0.2126 * red) + (0.7152 * green) + (0.0722 * blue)

    def contrast(self, color1, color2):
        """
        Calculate the contrast between two colors.
        """
        lum1 = self.luminance(color1)
        lum2 = self.luminance(color2)

        return (max(lum1, lum2) + 0.05) / (min(lum1, lum2) + 0.05)
    
    @commands.command(name="changecolor")
    async def changecolor(self, context, color):
        """
        Allows the user to change the color of their nickname. Only usable in some servers.
        """
        try:
            if context.message.guild.id != 856919397754470420 and context.message.guild.id != 850473081063211048:
                return
            
            limit = 4
            contrast = self.contrast("#36393f", color)

            if contrast < limit:
                embed = nextcord.Embed(
                    title="Error",
                    description="Color does not have enough contrast. That color has a contrast ratio of: " + str(round(contrast, 4)) + ":1. It needs to be above 4:1.",
                    color=int(color.replace("#", ""), 16)
                )
                await context.send(embed=embed)
                return
            userRoles = context.message.author.roles

            if len(userRoles) > 1:
                topRole = userRoles[-1]
                await topRole.edit(colour=nextcord.Colour(int(color.replace("#", ""), 16)))
                embed = nextcord.Embed(
                    title="Success!",
                    description="Color has been changed! The contrast it has is " + str(round(contrast, 4)) + ":1",
                    color=int(color.replace("#", ""), 16)
                )
                await context.send(embed=embed)
        except:
            embed = nextcord.Embed(
                title="Error",
                description="Something went wrong, make sure you are using a 6 digit hex code. (ex: !changecolor #FFFFFF)",
                color=config["error"]
            )
            await context.send(embed=embed)

    @commands.command(name="remindme")
    async def remindme(self, context, *args):
        """
        Has DadBot remind you at a specific time. 
        """
        mydb = mysql.connector.connect(
            host=config["dbhost"],
            user=config["dbuser"],
            password=config["dbpassword"],
            database=config["databasename"],
            autocommit=True
        )
        timeStr = " ".join(args).lower()
        time = dp.parse(timeStr, settings={'TIMEZONE': 'US/Eastern', 'RETURN_AS_TIMEZONE_AWARE': True, 'PREFER_DATES_FROM': 'future', 'PREFER_DAY_OF_MONTH': 'first'})
        timeWords = timeStr
        f = '%Y-%m-%d %H:%M:%S'
        if time is None:
            searchRes = search_dates(timeStr, settings={'TIMEZONE': 'US/Eastern', 'RETURN_AS_TIMEZONE_AWARE': True, 'PREFER_DATES_FROM': 'future', 'PREFER_DAY_OF_MONTH': 'first'}, languages=['en'])
            for t in searchRes:
                time = t[1]
                timeWords = t[0]
                break
            
        if time is not None:
            timeUTC = dp.parse(time.strftime(f), settings={'TIMEZONE': 'US/Eastern', 'TO_TIMEZONE': 'UTC'})
            mycursor = mydb.cursor(buffered=True)
            mycursor.execute("INSERT INTO reminders (author, message_id, remind_time) VALUES ('"+ str(context.message.author) +"', '"+ str(context.message.id) +"', '"+ timeUTC.strftime(f) +"')")

            await context.reply("You will be reminded at: " + time.strftime(f) + " EST \n\nHere's the time I read: " + timeWords)
            mydb.commit()
            mycursor.close()
            mydb.close()
        else:
            await context.reply("I can't understand that time, try again but differently")

    @commands.command(name="tldrchannel")
    async def tldrchannel(self, context, param):
        """
        Get a TLDR of X number of past messages on the channel.
        """
        if param.isnumeric() and int(param) >= 5:
            messages = await context.channel.history(limit=int(param)).flatten()
            text = ". ".join([m.content for m in messages])
            text = text.replace(".. ", ". ")
            embed = summarizer.getSummaryText(config, text)
        else:
            await context.reply(f'That number is either not a number or is less than 5. Try `{config["bot_prefix"]}tldrchannel 5` or higher')
            return

        await context.send(embed=embed)
    
    @commands.command(name="tldr")
    async def tldr(self, context, url):
        """
        Get the invite link of the bot to be able to invite it to another server.
        """
        try:
            await context.send(embed=summarizer.getSummaryUrl(config, url))
        except:
             await context.send("There's something odd about that link. Either they won't let me read it or you sent it wrongly.")


    @commands.command(name="invite")
    async def invite(self, context):
        """
        Get the invite link of the bot to be able to invite it to another server.
        """
        await context.send(f"Invite me by clicking here: https://discordapp.com/oauth2/authorize?&client_id={config['application_id']}&scope=bot&permissions=8")

    
    @commands.command(name="caught")
    async def caught(self, context):
        """
        See how many times everyone on the server has been caught by DadBot.
        """
        mydb = mysql.connector.connect(
            host=config["dbhost"],
            user=config["dbuser"],
            password=config["dbpassword"],
            database=config["databasename"]
        )
        mycursor = mydb.cursor(buffered=True)

        mycursor.execute("SELECT * FROM caught ORDER BY count DESC")

        res = "```\n"
        res += "{:38s} {:s}\n".format("Username", "Caught Count")
        res += ("-"*51) + "\n"
        for m in mycursor:
            res += "{:38s} {:d}\n".format(m[1], int(m[2]))
        res += "```"
        mycursor.close()
        mydb.close()
        await context.send(res)

    @commands.command(name="poll")
    async def poll(self, context, *args):
        """
        Create a poll where members can vote.
        """
        poll_title = " ".join(args)
        embed = nextcord.Embed(
            title="A new poll has been created!",
            description=f"{poll_title}",
            color=config["success"]
        )
        embed.set_footer(
            text=f"Poll created by: {context.message.author} • React to vote!"
        )
        embed_message = await context.send(embed=embed)
        await embed_message.add_reaction("👍")
        await embed_message.add_reaction("👎")
        await embed_message.add_reaction("🤷")

    @commands.command(name="8ball")
    async def eight_ball(self, context, *args):
        """
        Ask any question to the bot.
        """
        answers = ['It is certain.', 'It is decidedly so.', 'You may rely on it.', 'Without a doubt.',
                   'Yes - definitely.', 'As I see, yes.', 'Most likely.', 'Outlook good.', 'Yes.',
                   'Signs point to yes.', 'Reply hazy, try again.', 'Ask again later.', 'Better not tell you now.',
                   'Cannot predict now.', 'Concentrate and ask again later.', 'Don\'t count on it.', 'My reply is no.',
                   'My sources say no.', 'Outlook not so good.', 'Very doubtful.']
        embed = nextcord.Embed(
            title="**My Answer:**",
            description=f"{answers[random.randint(0, len(answers) - 1)]}",
            color=config["success"]
        )
        embed.set_footer(
            text=f"Question asked by: {context.message.author}"
        )
        await context.send(embed=embed)

    @commands.command(name="bitcoin")
    async def bitcoin(self, context):
        """
        Get the current price of bitcoin.
        """
        url = "https://api.coindesk.com/v1/bpi/currentprice/BTC.json"
        # Async HTTP request
        async with aiohttp.ClientSession() as session:
            raw_response = await session.get(url)
            response = await raw_response.text()
            response = json.loads(response)
            embed = nextcord.Embed(
                title=":information_source: Info",
                description=f"Bitcoin price is: ${response['bpi']['USD']['rate']}",
                color=config["success"]
            )
            await context.send(embed=embed)

def setup(bot):
    bot.add_cog(general(bot))
