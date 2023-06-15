import os
from functools import lru_cache
import tweepy


@lru_cache(maxsize=None)
def get_api():
    auth = tweepy.OAuth2BearerHandler(os.environ.get("TWITTER_BEARER_TOKEN"))
    api = tweepy.API(auth, parser=tweepy.parsers.JSONParser())
    return api


def search_users(q, count):
    api = get_api()
    users = api.search_users(q=q, count=count)
    extracted_users = []

    for user in users:
        screen_name = user["screen_name"]
        followers_count = user["followers_count"]
        statuses_count = user["statuses_count"]
        description = user["description"]
        profile_url = f"https://twitter/{screen_name}"
        lang = user["lang"]

        extracted_user = dict(
            screen_name=screen_name,
            profile_url=profile_url,
            description=description,
            followers_count=followers_count,
            statuses_count=statuses_count,
            lang=lang,
        )
        extracted_users.append(extracted_user)

    return extracted_users
