from step_one.prompts import summarize_reddit_post
import ray
from step_one.state_utils import add_tokens


def summarize_posts(posts):
    results = []
    for post in posts:
        results.append(summarize_post.remote(post))
    output = ray.get(results)
    summarized_posts = []
    for post, usage in output:
        summarized_posts.append(post)
        add_tokens(usage.prompt_tokens, usage.completion_tokens)
    return summarized_posts


@ray.remote
def summarize_post(post):
    summary, usage = summarize_reddit_post(post)
    post["summary"] = summary
    return post, usage
