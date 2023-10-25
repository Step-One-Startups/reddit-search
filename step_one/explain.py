from step_one.prompts import explain_relevance
import ray


def explain_posts_relevance(posts, need):
    try:
        ray.init()
        results = []
        for post in posts:
            results.append(explain_post_relevance.remote(post, need))
        output = ray.get(results)
    finally:
        ray.shutdown()
    return output


@ray.remote
def explain_post_relevance(post, need):
    summary = explain_relevance(post, need)
    post["explanation"] = summary
    return post
