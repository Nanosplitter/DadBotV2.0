import yaml
import sys
import os
import requests
import random

with open("./DadBot/config.yaml") as file:
    config = yaml.load(file, Loader=yaml.FullLoader)

class AntiMayhem:
    async def gotem(self, context):
        # Only reply to a specific user
        if context.author.id == 342927159968399370 and random.choice(range(20)) == 5:
            url = "https://evilinsult.com/generate_insult.php?lang=en&type=json"
            r = requests.get(url)
            json = r.json()
            await context.reply(json["insult"])