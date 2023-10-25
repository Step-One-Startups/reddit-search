from step_one.search import search_posts_raw
from step_one.filter import score_posts

from step_one.export import export_csv, export_json


keyphrases = [
    "walk",
    "walking alone",
    "unsafe walking",
    "danger when walking",
    "walking around by myself",
    "walk by myself",
]

DEFAULT_NEED = "Forming new habits is hard"

POSTS_TO_SEARCH = 50

for i in range(len(keyphrases)):
    keyphrases[i] = keyphrases[i].lower()


def find_posts(need: str = DEFAULT_NEED, log=print):
    raw_posts = search_posts_raw(need, None, POSTS_TO_SEARCH)
    log(f"Checking {len(raw_posts)} posts.")

    for post in raw_posts:
        post["need"] = need
        post["score"] = 0
        post["explanation"] = ""
        post["summary"] = ""

    posts = score_posts(raw_posts, need)
    log(f"Found {len(posts)} matching posts.")

    for post in posts:
        print(f"https://reddit.com{post['permalink']}")
        print(post["title"])
        if "selftext" in post:
            print(post["selftext"])
        post["need"] = need
        print(post)
        print()

    export_json(posts)

    return posts
