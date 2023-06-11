"""Reddit document loader."""
from __future__ import annotations

from typing import TYPE_CHECKING, Iterable, List, Optional, Sequence
from tqdm.auto import tqdm
from langchain.docstore.document import Document
from langchain.document_loaders.base import BaseLoader

if TYPE_CHECKING:
    import praw


def _dependable_praw_import() -> praw:
    try:
        import praw
    except ImportError:
        raise ValueError(
            "praw package not found, please install it with `pip install praw`"
        )
    return praw


class RedditPostsLoader(BaseLoader):
    """Reddit posts loader.
    Read posts on a subreddit.
    First you need to go to
    https://www.reddit.com/prefs/apps/
    and create your application
    """

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        user_agent: str,
        search_queries: Sequence[str],
        mode: str,
        categories: Sequence[str] = ["new"],
        number_posts: Optional[int] = 10,
        searchable_subreddits: Sequence[str] = ["all"],
    ):
        self.client_id = client_id
        self.client_secret = client_secret
        self.user_agent = user_agent
        self.search_queries = search_queries
        self.mode = mode
        self.categories = categories
        self.number_posts = number_posts
        self.searchable_subreddits = searchable_subreddits

    def load(self) -> List[Document]:
        """Load reddits."""
        praw = _dependable_praw_import()

        reddit = praw.Reddit(
            client_id=self.client_id,
            client_secret=self.client_secret,
            user_agent=self.user_agent,
        )

        results: List[Document] = []

        if self.mode == "subreddit":
            for search_query in self.search_queries:
                for category in self.categories:
                    docs = self._subreddit_posts_loader(
                        search_query=search_query, category=category, reddit=reddit
                    )
                    results.extend(docs)

        elif self.mode == "keyword":
            for search_query in self.search_queries:
                for category in self.categories:
                    docs = self._keyword_posts_loader(
                        search_query=search_query,
                        category=category,
                        reddit=reddit,
                    )
                    results.extend(docs)

        else:
            raise ValueError(
                "mode not correct, please enter 'username', 'subreddit' or 'keyword' as mode"
            )

        return results

    def _subreddit_posts_loader(
        self, search_query: str, category: str, reddit: praw.reddit.Reddit
    ) -> Iterable[Document]:
        subreddit = reddit.subreddit(search_query)
        method = getattr(subreddit, category)
        cat_posts = method(limit=self.number_posts)

        """Format reddit posts into a string."""
        for post in cat_posts:
            metadata = {
                "post_subreddit": post.subreddit_name_prefixed,
                "post_category": category,
                "post_title": post.title,
                "post_score": post.score,
                "post_id": post.id,
                "post_url": post.url,
                "post_author": post.author,
            }
            yield Document(
                page_content=post.selftext,
                metadata=metadata,
            )

    def _keyword_posts_loader(
        self, search_query: str, category: str, reddit: praw.reddit.Reddit
    ) -> Iterable[Document]:
        """Format reddit posts into a string."""
        documents = []
        for searchable_subreddit in self.searchable_subreddits:
            subreddit = reddit.subreddit(searchable_subreddit)

            for post in tqdm(
                subreddit.search(search_query, limit=self.number_posts, sort=category)
            ):
                body = post.selftext.strip()
                if body != "":
                    metadata = {
                        "post_subreddit": searchable_subreddit,
                        "post_category": category,
                        "post_title": post.title,
                        "post_score": post.score,
                        "post_id": post.id,
                        "post_url": post.url,
                        "post_author": post.author,
                        "is_comment": False,
                    }
                    # text_comments = [
                    #     post.title + "\n" + comment.body for comment in post.comments
                    # ]
                    main_document = Document(
                        page_content=post.title + "\n" + post.selftext,
                        metadata=metadata,
                    )
                    documents.append(main_document)

                    # metadata["is_comment"] = True

                    # for comment in post.comments:
                    #     text_comment = post.title + "\n" + comment.body
                    #     secondary_document = Document(
                    #         page_content=text_comment, metadata=metadata
                    #     )
                    #     documents.append(secondary_document)

        return documents
