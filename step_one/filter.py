from step_one.openAI import discern_applicability, summarize, score_post_relevance
import ray


def filter_by_keyphrase(posts, keyphrases):
    filtered_posts = []
    for i in range(len(posts)):
        posts[i]["index"] = i
    for post in posts:
        title = post["title"].lower()
        selftext = post["selftext"].lower()
        if any(keyphrase in title for keyphrase in keyphrases) or any(keyphrase in selftext for keyphrase in keyphrases):
            filtered_posts.append(post)
    return filtered_posts

def filter_by_need(posts, need):
    try:
        ray.init()
        results = [] 
        for post in posts:
            results.append(has_need.remote(post, need))
        output = ray.get(results)
        filtered_posts = [post for post in output if post]
    finally:
        ray.shutdown()
    return sorted(filtered_posts, key=lambda post: post["score"], reverse=True)

@ray.remote
def has_need(post, need):
    if discern_applicability(post, need):
        # Summarize the post on behalf of the user.
        post["summary"] = summarize(post, need)
        post["score"] = score_post_relevance(post, need)
        return post
    return None
