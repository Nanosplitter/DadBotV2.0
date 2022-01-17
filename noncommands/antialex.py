import yaml
import sys
import os
import uwuify

with open("config.yaml") as file:
    config = yaml.load(file, Loader=yaml.FullLoader)

class AntiMayhem:
    async def gotem(self, context):
        # Only reply to a specific user
        if context.author.id == 212384186672218112 and len(context.message.content) >= 100:
            message = await context.channel.fetch_message(context.message.reference.message_id)
            flags = uwuify.SMILEY | uwuify.YU
            await context.reply(uwuify.uwu(message.content, flags=flags))