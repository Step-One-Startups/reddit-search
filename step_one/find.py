from step_one.search import search_posts_raw
from step_one.score import score_posts
from step_one.summarize import summarize_posts
from step_one.explain import explain_posts_relevance
from step_one.export import export_csv, export_json
from step_one.state_utils import POSSIBLE_NEEDS
import streamlit as st

POSTS_TO_SEARCH = 100


def find_posts(need: str = POSSIBLE_NEEDS[0], log=print):
    raw_posts = search_posts_raw(need, None, POSTS_TO_SEARCH)
    log(f"Found {len(raw_posts)} posts.")
    log(f"Scoring posts on relevance.")

    for post in raw_posts:
        post["need"] = need
        post["score"] = 0
        post["explanation"] = ""
        post["summary"] = ""

    posts = score_posts(raw_posts, need)

    posts = sorted(posts, key=lambda post: post["score"], reverse=True)

    with st.expander("All scored posts"):
        st.dataframe(
            data=[
                {"link": post["permalink"], "score": post["score"]} for post in posts
            ],
            column_config={
                "link": st.column_config.LinkColumn("Reddit post"),
            },
            use_container_width=True,
            hide_index=True,
        )

    posts = [post for post in posts if post["score"] > 2]

    log(f"Summarizing {len(posts)} matching posts.")

    posts = summarize_posts(posts)

    posts = explain_posts_relevance(posts, need)

    # for post in posts:
    #     print(post['permalink'])
    #     print(post["title"])
    #     if "selftext" in post:
    #         print(post["selftext"])
    #     post["need"] = need
    #     print(post)
    #     print()

    export_json(posts)

    return posts
