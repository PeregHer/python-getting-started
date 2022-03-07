import re
import time
from collections import OrderedDict

import requests
import tweepy
from loguru import logger
import sys

API_KEY = "R5ynUeOq4FpX5Yg3TzCQo8W8I"
API_KEY_SECRET = "JGvdkpYmZI7BHg4cdeY2Xa6ekDXRLfXhWvKV8wxkb4StuL9RhI"
BEARER_TOKEN = "AAAAAAAAAAAAAAAAAAAAAOvqZwEAAAAAFWk9Z6jppW%2B7%2F%2Bx55oYn%2FTWf%2F%2BM%3DyohLDKOF4z2YVga16rvzGc4Kkysm6i7IscNomUdm07SGNofvuF"
ACCES_TOKEN = "1402233493-ieCsQtbDDYk0LRe5RGdXtOuVoU9LrWhRyaOgUGF"
ACCESS_TOKEN_SECRET = "Jv0uGszp5EOBmBeDUVBUd593yrLptXXFkA3Jvq6pdRSJS"


class Bot:
    def __init__(self, BEARER_TOKEN):
        self.client = tweepy.Client(BEARER_TOKEN)
        self.target_user = "ReyesClothes"
        self.webhook = "https://discord.com/api/webhooks/950507477328355370/k8DzcOQmR4zVVNFNJtYhGZDR7DfKjps6tRtVIzQyKcMIfI27pJm2BsziZUalA1mAl-Nr"
        logger.add(sys.stderr, format="{time} {level} {message}", filter="reyes", level="INFO")

        self.run()

    def get_last_tweet(self):
        query = f"from:{self.target_user} -is:retweet -is:reply"
        tweets = self.client.search_recent_tweets(query=query, max_results=10)
        return tweets[0][0]

    def check_codes(self, tweet):
        current_tweet = tweet.id
        logger.info(f"Found tweet {current_tweet}")
        if current_tweet == self.last_tweet:
            return None
        text = tweet.text
        pourcentages = set(re.findall(r"-[0-7]{2}%", text))

        codes = {}
        for pourcentage in pourcentages:
            nombres = pourcentage.replace("%", "").replace("-", "")
            code = re.search(fr"[a-zA-Z]+{nombres}", text)
            if code:
                codes[pourcentage] = code.group(0)
                
        self.last_tweet = current_tweet
        logger.info(f"Found {len(codes)} codes for tweet {current_tweet}")
        return OrderedDict(sorted(codes.items(), key=lambda t: t[0], reverse=True))

    def send_message(self, codes):

        message_codes = ""
        for code in codes:
            message_codes += f"{code} | {codes[code]}\n"

        content = {
            "content": "",
            "tts": "false",
            "embeds": [
                {
                    "title": f"{len(codes)} nouveaux codes trouvés !",
                    "description": message_codes,
                    "color": 1752220,
                    "fields": [
                        {
                            "name": "Consulter le Panier",
                            "value": "https://reyes-clothing.fr/fr/panier",
                            "inline": "true"
                        },
                        {
                            "name": "Consulter les produits",
                            "value": "https://reyes-clothing.fr/fr/13-nos-produits",
                            "inline": "true"
                        }
                    ],
                    "author": {
                        "name": "Reyes",
                        "icon_url": "https://pbs.twimg.com/profile_images/934547174779686919/XKIt3UwO_400x400.jpg"
                    }
                }
            ]
        }

        requests.post(self.webhook, json=content)
        logger.info(f"Sent message to Discord")

    def run(self):
        while True:
            tweet = self.get_last_tweet()
            codes = self.check_codes(tweet)
            if codes:
                self.send_message(codes)
            time.sleep(5)


if __name__ == "__main__":
    Bot(BEARER_TOKEN)
