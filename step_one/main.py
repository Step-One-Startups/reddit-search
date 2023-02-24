import json
import sys
from reddit.configuration import Configuration
from reddit.search import search_posts

from step_one.filter import filter_by_keyphrase, filter_by_need

problem = "I don't feel safe walking alone at night"

keyphrases = ["walk alone", "walking alone", "unsafe walking", "danger when walking", "walking around by myself", "walk by myself"]

for i in range(len(keyphrases)):
    keyphrases[i] = keyphrases[i].lower()

def find_posts():
    args = {
        "output": "posts.json",
        "verbose": True,
        "limit": 10000,
        "sort": "relevance",
        "make_hard_links": True,
        "subreddit": ["all"],
        "search": problem,
    }

    config = Configuration()
    config.process_arguments(args)

    posts = search_posts(config)

    posts = remove_duplicates(posts)
    
    posts = filter_by_keyphrase(posts, keyphrases)
    print(f"Found {len(posts)} posts after filtering by keyphrase.")

    posts = filter_by_need(posts, problem)
    print(f"Found {len(posts)} posts after filtering by need.")
    for post in posts:
        print(f"https://reddit.com{post['permalink']}")
        if "summary" in post:
            print(post["index"])
            print(post["summary"])
        # print(post)
        print()
            

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
        key = post["permalink"]
        if key not in seen:
            seen.add(key)
            result.append(post)
    return result