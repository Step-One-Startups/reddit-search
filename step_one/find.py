import json
import sys
from reddit.configuration import Configuration
from reddit.search import search_posts, search_posts_raw

from step_one.filter import filter_by_keyphrase, filter_by_need, filter_subreddits
from step_one.openAI import restate_need


keyphrases = ["walk", "walking alone", "unsafe walking", "danger when walking", "walking around by myself", "walk by myself"]

NUM_POSTS_INCLUDED_PURELY_BY_RELEVANCE = 10

for i in range(len(keyphrases)):
    keyphrases[i] = keyphrases[i].lower()

def find_posts(provided_need: str, log=print):
    need = provided_need or "Protect oneself from government surveillance."
    need_from_user_perspective = restate_need(need)
    log("restated need:", need_from_user_perspective)
    # need_from_user_perspective = "I want to develop new habits."
    # subreddit_relevance_question = f"Could this subreddit have any connection at all to the following problem? {need}"
    # relevance_question = f"Does this person have a problem that is closely related to this one? {need}"

    
    # args = {
    #     "verbose": True,
    #     "limit": 10,
    #     "sort": "relevance",
    #     "make_hard_links": True,
    #     # "subreddit": ["all"],
    #     "search": need_from_user_perspective,
    # }

    # config = Configuration()
    # config.process_arguments(args)

    # first_round_posts = search_posts(config)
    first_round_posts = search_posts_raw(need_from_user_perspective)
    log(f"Found {len(first_round_posts)} posts (after removing duplicates).")

    # for post in first_round_posts:
    #     print(f"https://reddit.com{post['permalink']}")
    #     print(post["title"])
    #     print(post["selftext"][:1000])

    #     print("\n\n")

    # first_round_posts = search_subreddits(config, relevance_question)
    # print(f"Found {len(first_round_posts)} posts after filtering by need (round 1).")

    # subreddit = filter_subreddits(first_round_posts, subreddit_relevance_question)

    # print("subreddits: ", subreddit)
    # config.subreddit = subreddit
    # config.limit = 100

    # second_round_posts = search_subreddits(config, definite_question)

    posts = filter_by_need(first_round_posts, need)
    log(f"Found {len(posts)} posts after filtering by need.")

    for post in posts:
        print(f"https://reddit.com{post['permalink']}")
        if "summary" in post:
            # print(post["index"])
            print(post["summary"])
        # print(post)
        print()
    return posts

def search_subreddits(config: Configuration, question: str):
    original_posts = search_posts(config)

    most_relevant_posts = original_posts[:NUM_POSTS_INCLUDED_PURELY_BY_RELEVANCE]
    less_relevant_posts = original_posts[NUM_POSTS_INCLUDED_PURELY_BY_RELEVANCE:]
    
    less_relevant_posts = filter_by_keyphrase(less_relevant_posts, keyphrases)
    print(f"Found {len(less_relevant_posts)} posts after filtering by keyphrase.")

    # Add the most relevant posts to the list, even if they don't contain the keyphrase
    posts = most_relevant_posts + less_relevant_posts

    return filter_by_need(posts, question)
            