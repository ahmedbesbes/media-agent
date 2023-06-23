"""Twitter document loader."""
from __future__ import annotations
from typing import TYPE_CHECKING, Any, Dict, Iterable, List, Optional, Sequence, Union

from langchain.docstore.document import Document
from langchain.document_loaders.base import BaseLoader

from src.utils.search import (
    search_tweets_by_keywords,
    search_tweets_by_usernames,
)

if TYPE_CHECKING:
    import tweepy
    from tweepy import OAuth2BearerHandler, OAuthHandler


def _dependable_tweepy_import() -> tweepy:
    try:
        import tweepy
    except ImportError:
        raise ValueError(
            "tweepy package not found, please install it with `pip install tweepy`"
        )
    return tweepy


class TwitterTweetLoader(BaseLoader):
    """Twitter tweets loader.
    Read tweets of user twitter handle.

    First you need to go to
    `https://developer.twitter.com/en/docs/twitter-api
    /getting-started/getting-access-to-the-twitter-api`
    to get your token. And create a v2 version of the app.
    """

    def __init__(
        self,
        auth_handler: Union[OAuthHandler, OAuth2BearerHandler],
        twitter_users: Union[Sequence[str], None],
        keywords: Union[str, None],
        number_tweets: Optional[int] = 100,
    ):
        self.auth = auth_handler
        self.twitter_users = twitter_users
        self.number_tweets = number_tweets
        self.keywords = keywords

        if self.keywords is None and self.twitter_users is None:
            raise ValueError("You should set keywords or twitter_users, not both.")
        if self.keywords is not None:
            self.search_mode = "keywords"
        else:
            self.search_mode = "twitter_users"

    def load(self):
        """Load tweets."""
        tweepy = _dependable_tweepy_import()
        api = tweepy.API(self.auth, parser=tweepy.parsers.JSONParser())

        results: List[Document] = []

        if self.search_mode == "twitter_users":
            tweets = search_tweets_by_usernames(
                api,
                self.twitter_users,
                self.number_tweets,
            )
        elif self.search_mode == "keywords":
            tweets = search_tweets_by_keywords(
                api,
                self.keywords,
                self.number_tweets,
            )

        results = self._format_tweets(tweets)
        return results

    def _format_tweets(self, tweets: List[Dict[str, Any]]):
        """Format tweets into a string."""
        documents = []
        for tweet in tweets:
            metadata = {
                "created_at": tweet["created_at"],
                "tweet_id": tweet["id"],
            }

            document = Document(
                page_content=tweet["full_text"],
                metadata=metadata,
            )
            documents.append(document)
        return documents

    @classmethod
    def from_bearer_token(
        cls,
        oauth2_bearer_token: str,
        twitter_users: Sequence[str],
        keywords: Union[str, None],
        number_tweets: Optional[int] = 100,
    ) -> TwitterTweetLoader:
        """Create a TwitterTweetLoader from OAuth2 bearer token."""
        tweepy = _dependable_tweepy_import()
        auth = tweepy.OAuth2BearerHandler(oauth2_bearer_token)
        return cls(
            auth_handler=auth,
            twitter_users=twitter_users,
            keywords=keywords,
            number_tweets=number_tweets,
        )

    @classmethod
    def from_secrets(
        cls,
        access_token: str,
        access_token_secret: str,
        consumer_key: str,
        consumer_secret: str,
        twitter_users: Sequence[str],
        keywords: Union[str, None],
        number_tweets: Optional[int] = 100,
    ) -> TwitterTweetLoader:
        """Create a TwitterTweetLoader from access tokens and secrets."""
        tweepy = _dependable_tweepy_import()
        auth = tweepy.OAuthHandler(
            access_token=access_token,
            access_token_secret=access_token_secret,
            consumer_key=consumer_key,
            consumer_secret=consumer_secret,
        )
        return cls(
            auth_handler=auth,
            twitter_users=twitter_users,
            keywords=keywords,
            number_tweets=number_tweets,
        )
