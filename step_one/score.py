from step_one.prompts import score_post_relevance
import ray
from step_one.state_utils import record_score


def score_posts(posts, need):
    try:
        ray.init(ignore_reinit_error=True)
        results = []
        for post in posts:
            results.append(score_post.remote(post, need))
        output = ray.get(results)
    finally:
        ray.shutdown()
    return output


@ray.remote
def score_post(post, need):
    score = score_post_relevance(post, need)
    post["score"] = score

    return post
