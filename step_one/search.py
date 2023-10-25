from typing import List
from step_one.logger import logger
import requests


def search_posts_raw(
    problem: str, subreddit: str = None, num_posts_to_include: int = 5
):
    subreddit_extension = f"r/{subreddit}/" if subreddit is not None else ""
    posts = []
    try:
        response = requests.get(
            f"http://www.reddit.com/{subreddit_extension}search.json?q={problem}&limit={num_posts_to_include}&restrict_sr=on",
            headers={"User-agent": "step-one bot 0.1"},
        ).json()
        raw_posts = response["data"]["children"]

        for raw_post in raw_posts:
            posts.append(
                {
                    # Add key to remove duplicates
                    "key": raw_post["data"]["title"]
                    + raw_post["data"]["selftext"][:100],
                    "title": raw_post["data"]["title"],
                    "subreddit": raw_post["data"]["subreddit"],
                    "selftext": raw_post["data"]["selftext"],
                    "permalink": f"https://reddit.com{raw_post['data']['permalink']}",
                }
            )
    except Exception:
        logger.exception("search_posts_raw exited unexpectedly")
        raise
    else:
        logger.info("Search complete")
        return remove_duplicates(posts)


def remove_duplicates(list: List[dict]):
    seen = set()
    result = []
    for item in list:
        key = item["key"]
        if key not in seen:
            seen.add(key)
            result.append(item)
    return result
