from langchain.llms import OpenAI
from step_one.prompts import extract_need_prompt, discern_applicability_prompt, filter_subreddit_prompt
import ray
import praw
import socket

CURIE_MAX_INPUT_TOKENS = 2048 - 256

curie_llm = OpenAI(model_name="text-curie-001", temperature=0)
davinci_llm = OpenAI(model_name="text-davinci-003", temperature=0)


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

def filter_by_need(posts, question):
    ray.init()
    results = [] 
    for post in posts:
        results.append(has_need.remote(post, question))
    output = ray.get(results)
    ray.shutdown()
    filtered_posts = [post for post in output if post]

    return filtered_posts

@ray.remote
def has_need(post, question):
    post["summary"] = extract_need(post)
    if post["summary"] != "" and states_need(post, question):
        return post
    return None


def extract_need(post):
    try:
        post_content = post["selftext"] or "No content"
        formatted_extract_need_prompt = extract_need_prompt.format(
            title=post["title"],
            selftext=post_content
        )
        return curie_llm(formatted_extract_need_prompt).strip()
    except:
        return ""

def states_need(post, question):
    formatted_discern_applicability_prompt = discern_applicability_prompt.format(
        title=post["title"],
        summary=post["summary"],
        question=question
    )
    full_answer = davinci_llm(formatted_discern_applicability_prompt).strip()
    post["full_answer"] = full_answer
    print("\n\n")
    print(f"https://reddit.com{post['permalink']}")
    print(post["summary"])
    print(formatted_discern_applicability_prompt)
    print(full_answer)
    answer = full_answer.lower().split("answer:")[1].strip()
    # print(answer)
    return len(answer) >= 4 and answer[0:4] == "true"

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

@ray.remote
def subreddit_is_relevant(subreddit_info, question):
    formatted_discern_filter_subreddit_prompt = filter_subreddit_prompt.format(
        subreddit=subreddit_info["name"],
        subreddit_description=subreddit_info["description"],
        question=question
    )
    full_answer = davinci_llm(formatted_discern_filter_subreddit_prompt).strip()
    print(subreddit_info["name"])
    print(subreddit_info["description"])
    print(full_answer)
    answer = full_answer.lower().split("answer:")[1].strip()
    if len(answer) >= 4 and answer[0:4] == "true":
        return subreddit_info["name"]
    return None
