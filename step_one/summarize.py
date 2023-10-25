from step_one.prompts import summarize_reddit_post
import ray


def summarize_posts(posts):
    try:
        ray.init()
        results = []
        for post in posts:
            results.append(summarize_post.remote(post))
        output = ray.get(results)
    finally:
        ray.shutdown()
    return output


@ray.remote
def summarize_post(post):
    summary = summarize_reddit_post(post)
    post["summary"] = summary
    return post
