from typing import List
from reddit.archiver import Archiver
from reddit.configuration import Configuration
from reddit.bdfr.logger import make_console_logging_handler, silence_module_loggers, logger
import requests
import ray

from step_one.openAI import score_subreddit_relevance


def search_posts(config: Configuration):
    silence_module_loggers()
    stream = make_console_logging_handler(config.verbose)
    posts = []
    try:
        reddit_archiver = Archiver(config, [stream])
        posts = reddit_archiver.download()
    except Exception:
        logger.exception("Archiver exited unexpectedly")
        raise
    else:
        logger.info("Search complete")
        return posts

def search_posts_raw(problem: str, subreddit: str = None, num_posts_to_include: int = 5):
    subreddit_extension = f"r/{subreddit}/" if subreddit is not None else ""
    posts = []
    try:
        response = requests.get(
            f"http://www.reddit.com/{subreddit_extension}search.json?q={problem}&limit={num_posts_to_include}&restrict_sr=on",
            headers = {'User-agent': 'step-one bot 0.1'}
        ).json()
        raw_posts = response["data"]["children"]
        # print(posts)
        # print("\n\n\n")
        for raw_post in raw_posts:
            posts.append({
                # Add key to remove duplicates
                "key": raw_post["data"]["title"] + raw_post["data"]["selftext"][:100],
                "title": raw_post["data"]["title"],
                "subreddit": raw_post["data"]["subreddit"],
                "selftext": raw_post["data"]["selftext"],
                "permalink": raw_post["data"]["permalink"],
            })
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

def search_subreddits(need: str, user_groups: List[str] = []):
    subreddits = []

    try:
        for user_group in user_groups:
            response = requests.get(
                f"http://www.reddit.com/subreddits/search.json?q={user_group}&limit=5",
                headers = {'User-agent': 'step-one bot 0.1'}
            ).json()
            raw_subreddits = response["data"]["children"]
            for raw_subreddit in raw_subreddits:
                subreddits.append({
                    "key": raw_subreddit["data"]["display_name"],
                    "name": raw_subreddit["data"]["display_name"],
                    "description": raw_subreddit["data"]["public_description"],
                    "subscribers": raw_subreddit["data"]["subscribers"],
                    "url": raw_subreddit["data"]["url"],
                })
        subreddits = remove_duplicates(subreddits)
    except Exception:
        logger.exception("search_subreddits exited unexpectedly")
        raise
    finally:
        logger.info("Search complete")
        # return three most relevant subreddits
        return rank_subreddits(subreddits, need)[:6]
    
def rank_subreddits(subreddits, need):
    # Rank subreddits by how relevant they are to the need
    try:
        ray.init()
        results = []
        for subreddit in subreddits:
            results.append(score_subreddit_relevance.remote(subreddit, need))
        output = ray.get(results)
    finally:
        ray.shutdown()
    return sorted(output, key=lambda x: x["score"], reverse=True)