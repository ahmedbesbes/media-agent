"""Twitter document loader."""
from __future__ import annotations
import os
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Sequence, Union

from datetime import datetime
from praw import Reddit
from praw.models import Submission, MoreComments, Comment
from rich.console import Console
from contextlib import nullcontext

from langchain.docstore.document import Document

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


class DocumentLoader(ABC):
    @property
    @abstractmethod
    def source(self) -> str:
        pass

    @abstractmethod
    def _load(self) -> List[Document]:
        pass

    @abstractmethod
    def _get_search_params(self) -> Dict[str, Any]:
        pass

    def load(
        self,
        console: Optional[Console] = None,
        history: Optional[Dict[str, Any]] = None,
    ) -> List[Document]:
        """Load documents."""

        context = (
            nullcontext
            if console is None
            else console.status(
                "Loading Documents",
                spinner="aesthetic",
                speed=1.5,
                spinner_style="red",
            )
        )

        with context:
            documents = self._load()

        if history:
            history["search_params"] = self._get_search_params()
            history["num_documents"] = len(documents)
            history["source"] = self.source

        return documents


class TwitterTweetLoader(DocumentLoader):
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
        number_tweets: int,
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

    @property
    def source(self) -> str:
        return "twitter"

    def _load(self):
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

    def _get_search_params(self) -> Dict[str, Any]:
        ret = dict(
            number_tweets=self.number_tweets,
            search_mode=self.search_mode,
        )

        if self.search_mode == "twitter_users":
            ret["twitter_users"] = self.twitter_users
        else:
            ret["keywords"] = self.keywords

        return ret

    def _format_tweets(self, tweets: List[Dict[str, Any]]):
        """Format tweets into a string."""
        documents = []
        for tweet in tweets:
            metadata = {
                "created_at": tweet["created_at"],
                "tweet_id": tweet["id"],
                "source": tweet["id"],
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
        number_tweets: int,
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
        number_tweets: int,
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


class RedditSubLoader(DocumentLoader):
    def __init__(
        self,
        number_submissions: int,
        subreddits: Optional[List[str]] = None,
        keywords: Optional[List[str]] = None,
    ):
        self.reddit = Reddit(
            client_id=os.environ.get("REDDIT_API_CLIENT_ID"),
            client_secret=os.environ.get("REDDIT_API_SECRET"),
            user_agent=os.environ.get("REDDIT_USER_AGENT"),
        )

        self.subreddits = subreddits
        self.keywords = keywords
        self.number_submissions = number_submissions

        if self.keywords is None and self.subreddits is None:
            raise ValueError("You should at least one of keywords or subreddits")
        if self.keywords is not None:
            self.search_mode = "keywords"
        else:
            self.search_mode = "subreddits"

    @property
    def source(self) -> str:
        return "reddit"

    def _load(self) -> List[Document]:
        """Load submissions."""

        if self.search_mode == "subreddits":
            submissions = self._search_subreddits()
        elif self.search_mode == "keywords":
            submissions = self._search_keywords()

        documents = self._format_submissions(submissions)
        return documents

    def _format_submissions(self, submissions: List[Submission]) -> List[Document]:
        ret = []

        for sub in submissions:
            ret.append(self._format_submission(sub))

            for comment in sub.comments.list():
                ret.append(self._format_comment(comment))

        return ret

    def _format_submission(self, submission: Submission) -> Document:
        """Format a submission into a Document"""

        return Document(
            page_content="\n".join([submission.title, submission.selftext]),
            metadata=dict(
                id=submission.id,
                upvotes=submission.ups,
                permalink="reddit.com" + submission.permalink,
                created_utc=datetime.fromtimestamp(submission.created_utc),
                author_karma=submission.author.comment_karma,
                contains_url=submission.url is not None and len(submission.url) > 0,
                contains_media=submission.media is not None
                and len(submission.media) > 0,
            ),
        )

    def _format_comment(self, comment: Comment) -> Document:
        """Format a comment into a Document"""

        submission = comment.submission
        author = comment.author

        page_content = f"""
To the post '{submission.title}' with {submission.ups} upvotes,
a redditor with a karma count of {author.comment_karma} posted a comment which gathered {comment.ups} upvotes:
```
{comment.body}
```
"""
        return Document(
            page_content=page_content,
            metadata=dict(
                id=comment.id,
                upvotes=comment.ups,
                permalink="reddit.com" + comment.permalink,
                created_utc=datetime.fromtimestamp(comment.created_utc),
                author_karma=author.comment_karma,
            ),
        )

    def _search_subreddits(self) -> List[Submission]:
        """Fetch Daily top submissions from subreddidts.

        Returns
        -------
        List[Submission]
            list of submissions
        """

        subreddit = self.reddit.subreddit("+".join(self.subreddits))
        return list(subreddit.top(limit=self.number_submissions, time_filter="day"))

    def _search_keywords(self) -> List[Submission]:
        subreddit = self.reddit.subreddit("all")
        return list(subreddit.search(self.keywords, limit=self.number_submissions))

    def _get_search_params(self) -> Dict[str, Any]:
        ret = dict(
            number_submissions=self.number_submissions,
            search_mode=self.search_mode,
        )

        if self.search_mode == "subreddits":
            ret["subreddits"] = self.subreddits
        else:
            ret["keywords"] = self.keywords

        return ret
