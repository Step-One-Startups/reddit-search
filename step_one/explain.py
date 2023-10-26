from step_one.prompts import explain_relevance
import ray
from step_one.state_utils import add_tokens


def explain_posts_relevance(posts, need):
    results = []
    for post in posts:
        results.append(explain_post_relevance.remote(post, need))
    output = ray.get(results)
    explained_posts = []
    for post, usage in output:
        explained_posts.append(post)
        add_tokens(usage.prompt_tokens, usage.completion_tokens)
    return explained_posts


@ray.remote
def explain_post_relevance(post, need):
    summary, usage = explain_relevance(post, need)
    post["explanation"] = summary
    return post, usage
