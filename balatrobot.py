import praw
import pprint
import re
import json
import string
from dataclasses import dataclass

@dataclass
class Card:
    name: str
    ctype: str
    effect: str
    rarity: str
    cost: int
    unlock: str
    link: str
    notes: str

cardlist = []

with open('balatrobot.json', 'r', encoding='utf-8',) as f:
    data = json.load(f)

for i in data:
    c = Card(i["name"], i["type"], i["effect"], i["rarity"], i["cost"], i["unlock"], i["link"], i["notes"])
    cardlist.append(c)

# Regular expression to match content between [[ and ]]
pattern = r"\[\[(.*?)\]\]"

reddit = praw.Reddit("balatro-bot-revived", user_agent="Balatro Bot Revived 0.0.1 (by /u/TheBouncerr)")

balatro = reddit.subreddit("testingground4bots")
balatrostream = balatro.stream.comments()

def generate_comment(c):
    body = "#**[" + c.name + "](" + c.link + ")** | " + c.ctype + "  \n\n"
    if c.cost != 0 and c.ctype != "Blind":
        body += "* Cost: $" + str(c.cost) + "  \n\n"
    elif c.cost != 0 and c.ctype == "Blind":
        body += "* Score at least " + str(c.cost / 10) + "x base  \n\n"
    if c.rarity != "N/A":
        body += "* Rarity: " + c.rarity + "  \n\n"
    body += "* Effect: " + c.effect + "  \n\n"
    if c.unlock != "N/A":
        body += "* Unlock Requirement: " + c.unlock + "  \n"
    if c.notes != "N/A":
        body += "* Notes: " + c.notes + "  \n"
    return (body)

reply_body = ""
footer = "  \n\n*Made by [\\/u/TheBouncerr](https://www.reddit.com/user/TheBouncerr/), info from the [Balatro Wiki](https://balatrogame.fandom.com)*"
joker_comment = ""

for comment in balatrostream:
    if comment.author.name == "balatro-bot-revived" or comment.author.name == "balatro-bot" or comment.saved:
        continue
    #print("comment : " + comment.body)
    comment.save()
    matches = re.findall(pattern, comment.body)
    if (matches):
        #print("potential matches found")
        for match in matches:
            print("match : " + match)
            joker = next((card for card in cardlist if card.name == string.capwords(match)), None)
            if joker:
                #print("found match for " + match)
                joker_comment = generate_comment(joker)
                #print("generated comment for " + match)
                if reply_body == "":
                    reply_body = joker_comment
                else:
                    if (len(reply_body) + len(joker_comment) + len(footer) <= 10000):
                        reply_body += "  \n\n" + generate_comment(joker)
            else:
                #print("No match for " + match)
                pass
        if reply_body:
            print("replying")
            reply_body += "  \n\n*Made by [\\/u/TheBouncerr](https://www.reddit.com/user/TheBouncerr/), info from the [Balatro Wiki](https://balatrogame.fandom.com)*"
            comment.reply(reply_body)
            reply_body = ""