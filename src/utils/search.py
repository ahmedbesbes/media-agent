import os
from functools import lru_cache
import tweepy
from src import logger
from src.utils.config import BLACKLIST, SEARCH_FILTERS


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


def search_tweets_by_usernames(api: tweepy.API, twitter_users, number_tweets):
    tweets = []
    for username in twitter_users:
        tweets_by_username = api.user_timeline(
            screen_name=username,
            count=number_tweets,
            tweet_mode="extended",
        )
        tweets.extend(tweets_by_username)
    return tweets


def prepare_query(keywords):
    q = f"{keywords}"

    for black_listed_kw in BLACKLIST:
        q += f" -{black_listed_kw}"

    for filter in SEARCH_FILTERS:
        q += f" -filter:{filter}"

    logger.info(f"prepared query : {q}")
    return q


def search_tweets_by_keywords(api: tweepy.API, keywords, number_tweets):
    q = prepare_query(keywords)
    tweets = api.search_tweets(
        q=q,
        count=number_tweets,
        tweet_mode="extended",
        lang="en",
    )
    tweets = tweets["statuses"]

    return tweets
