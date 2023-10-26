from step_one.search import search_posts_raw
from step_one.score import score_posts
from step_one.summarize import summarize_posts
from step_one.explain import explain_posts_relevance
from step_one.export import export_csv, export_json
from step_one.state_utils import POSSIBLE_NEEDS, clear_usage, get_usage
import streamlit as st
import ray

POSTS_TO_SEARCH = 100


def find_posts(need: str = POSSIBLE_NEEDS[0], log=print):
    try:
        print("called find_posts")
        ray.init(ignore_reinit_error=True)
        clear_usage()
        log(f"Searching reddit...")
        raw_posts = search_posts_raw(need, None, POSTS_TO_SEARCH)
        log(f"Found {len(raw_posts)} posts.")
        log(f"Scoring posts on relevance.")

        for post in raw_posts:
            post["need"] = need
            post["score"] = 0
            post["explanation"] = ""
            post["summary"] = ""

        posts = score_posts(raw_posts, need)

        usage = get_usage()

        print(usage)

        posts = sorted(posts, key=lambda post: post["score"], reverse=True)

        with st.expander("Post relevance scores (click to expand)"):
            st.dataframe(
                data=[
                    {"link": post["permalink"], "score": post["score"]}
                    for post in posts
                ],
                column_config={
                    "link": st.column_config.LinkColumn("Reddit post"),
                },
                use_container_width=True,
                hide_index=True,
            )

        posts = [post for post in posts if post["score"] > 2]

        log(f"Summarizing {len(posts)} relevant posts.")

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

        usage = get_usage()
        # return usage here to ensure that it's cached
        return posts, usage["prompt_tokens"], usage["completion_tokens"]
    finally:
        ray.shutdown()
