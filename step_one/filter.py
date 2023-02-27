from step_one.openAI import discern_applicability, extract_need, extract_need_prompt, discern_applicability_prompt, filter_subreddit_prompt, subreddit_is_relevant
import ray
import praw
import socket



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

    return filtered_posts

@ray.remote
def has_need(post, question):
    post["summary"] = extract_need(post)
    if post["summary"] != None and discern_applicability(post, question):
        return post
    return None


def filter_subreddits(posts, question):
    reddit_instance = praw.Reddit(
        client_id="U-6gk4ZCh3IeNQ",
        client_secret="7CZHY6AmKweZME5s50SfDGylaPg",
        user_agent=socket.gethostname(),
    )
    pending_subreddit_names = []
    pending_subreddits = []
    for post in posts:
        if post["subreddit"] not in pending_subreddit_names:
            pending_subreddit_names.append(post["subreddit"])
            subreddit = praw.models.Subreddit(reddit_instance, post["subreddit"])
            print(subreddit.display_name)
            print(subreddit.public_description)
            pending_subreddits.append({
                "name": post["subreddit"],
                "description": subreddit.public_description,
            })
    print("pending_subreddits:", pending_subreddits)
    ray.init()
    results = []
    for subreddit in pending_subreddits:
        results.append(subreddit_is_relevant.remote(subreddit, question))
    output = ray.get(results)
    ray.shutdown()
    filtered_subreddits = [subreddit for subreddit in output if subreddit]
    return filtered_subreddits
