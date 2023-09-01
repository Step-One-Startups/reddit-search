from step_one.search import search_posts_raw
from step_one.filter import score_posts

from step_one.export import export_csv, export_json



keyphrases = ["walk", "walking alone", "unsafe walking", "danger when walking", "walking around by myself", "walk by myself"]

DEFAULT_NEED = "Forming new habits is hard"

TOTAL_POSTS_TO_SEARCH = 50

for i in range(len(keyphrases)):
    keyphrases[i] = keyphrases[i].lower()

def find_posts(need:str=DEFAULT_NEED, log=print):

    first_round_posts = []
    first_round_posts += search_posts_raw(need, None, 30)
    log(f"Checking {len(first_round_posts)} posts.")

    for post in first_round_posts:
        post['need'] = need
        post['score'] = 0
        post['full_answer'] = ""
    
    # export_json(first_round_posts)
    # return first_round_posts

    posts = score_posts(first_round_posts, need)
    log(f"Found {len(posts)} posts.")

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
