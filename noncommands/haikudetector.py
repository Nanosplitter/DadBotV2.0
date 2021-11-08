import re
import yaml
import sys
import os

if not os.path.isfile("config.yaml"):
    sys.exit("'config.yaml' not found! Please add it and try again.")
else:
    with open("config.yaml") as file:
        config = yaml.load(file, Loader=yaml.FullLoader)



def sylco(word):
    VOWEL_RUNS = re.compile("[aeiouy]+", flags=re.I)
    EXCEPTIONS = re.compile(
        # fixes trailing e issues:
        # smite, scared
        "[^aeiou]e[sd]?$|"
        # fixes adverbs:
        # nicely
        + "[^e]ely$",
        flags=re.I
    )
    ADDITIONAL = re.compile(
        # fixes incorrect subtractions from exceptions:
        # smile, scarred, raises, fated
        "[^aeioulr][lr]e[sd]?$|[csgz]es$|[td]ed$|"
        # fixes miscellaneous issues:
        # flying, piano, video, prism, fire, evaluate
        + ".y[aeiou]|ia(?!n$)|eo|ism$|[^aeiou]ire$|[^gq]ua",
        flags=re.I
    )

    vowel_runs = len(VOWEL_RUNS.findall(word))
    exceptions = len(EXCEPTIONS.findall(word))
    additional = len(ADDITIONAL.findall(word))
    return max(1, vowel_runs - exceptions + additional)




def popNumSyl(syl, words):
    res = []
    while syl > 0 and len(words) > 0:
        word = words.pop()
        res.append(word)
        syl -= sylco(word)

    return (syl == 0, res, words)

class HaikuDetector:
    async def checkForHaiku(self, message):
        text = message.content
        words = text.split()[::-1]
        poem = []
        if sylco(text) == 17:
            lines = [5, 7, 5]
            for syl in lines:
                res = popNumSyl(syl, words)
                words = res[2].copy()
                poem.append(res)
            if all([i[0] for i in poem]):
                res = "You're a poet!\n\n"
                for line in [i[1] for i in poem]:
                    res += "*" + " ".join(line) + "*\n"
                res += "\n -" + message.author.mention
                await message.reply(res)