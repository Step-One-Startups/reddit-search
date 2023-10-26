from step_one.prompts import score_post_relevance
import ray
from step_one.state_utils import add_tokens


def score_posts(posts, need):
    results = []
    for post in posts:
        results.append(score_post.remote(post, need))
    output = ray.get(results)
    scored_posts = []
    for post, usage in output:
        scored_posts.append(post)
        add_tokens(usage.prompt_tokens, usage.completion_tokens)

    return scored_posts


@ray.remote
def score_post(post, need):
    score, usage = score_post_relevance(post, need)
    post["score"] = score

    print("scored post: ", post["permalink"], post["score"])

    return post, usage
