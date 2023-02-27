from typing import List
from reddit.archiver import Archiver
from reddit.configuration import Configuration
from reddit.bdfr.logger import make_console_logging_handler, silence_module_loggers, logger
import requests


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

def search_posts_raw(problem: str):
    posts = []
    try:
        search_string = f"http://www.reddit.com/search.json?q={problem}&limit=50"
        print(search_string)
        response = requests.get(search_string, headers = {'User-agent': 'step-one bot 0.1'}).json()
        raw_posts = response["data"]["children"]
        # print(posts)
        # print("\n\n\n")
        print(raw_posts[0]["data"].keys())
        for raw_post in raw_posts:
            posts.append({
                # Add key to remove duplicates
                "key": raw_post["data"]["author"] + raw_post["data"]["title"],
                "title": raw_post["data"]["title"],
                "subreddit": raw_post["data"]["subreddit"],
                "selftext": raw_post["data"]["selftext"],
                "permalink": raw_post["data"]["permalink"],
            })
        print(raw_posts[0]["data"]["subreddit"])
    except Exception:
        logger.exception("search_posts_raw exited unexpectedly")
        raise
    else:
        logger.info("Search complete")
        return remove_duplicates(posts)

def remove_duplicates(posts):
    """
    Removes duplicates from a list based on a key function.

    :param lst: The list to remove duplicates from.
    :param key_func: The function to extract the key from each item in the list.
    :return: A list containing only the unique items.
    """
    seen = set()
    result = []
    for post in posts:
        # Some posts might have the same title, but different selftext
        key = post["key"]
        if key not in seen:
            seen.add(key)
            result.append(post)
    return result