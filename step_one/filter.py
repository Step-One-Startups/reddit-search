from step_one.prompts import score_post_relevance, summarize_post
import ray


def filter_by_keyphrase(posts, keyphrases):
    filtered_posts = []
    for i in range(len(posts)):
        posts[i]["index"] = i
    for post in posts:
        title = post["title"].lower()
        selftext = post["selftext"].lower()
        if any(keyphrase in title for keyphrase in keyphrases) or any(
            keyphrase in selftext for keyphrase in keyphrases
        ):
            filtered_posts.append(post)
    return filtered_posts


def score_posts(posts, need):
    try:
        ray.init()
        results = []
        for post in posts:
            results.append(score_post.remote(post, need))
        output = ray.get(results)
        filtered_posts = [post for post in output if post]
    finally:
        ray.shutdown()
    return sorted(filtered_posts, key=lambda post: post["score"], reverse=True)


@ray.remote
def score_post(post, need):
    explanation, score = score_post_relevance(post, need)
    post["explanation"] = explanation
    post["score"] = score

    if score < 5:
        return None

    summary = summarize_post(post)
    post["summary"] = summary
    return post
