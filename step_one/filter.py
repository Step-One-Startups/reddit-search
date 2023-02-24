from langchain.llms import OpenAI
from step_one.prompts import extract_need_prompt, discern_applicability_prompt
import ray

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

def filter_by_need(posts, problem):
    ray.init()
    results = [] 
    for post in posts:
        results.append(has_need.remote(post, problem))
    output = ray.get(results)
    filtered_posts = [post for post in output if post]

    return filtered_posts

@ray.remote
def has_need(post, problem):
    post["summary"] = extract_need(post)
    if post["summary"] != "" and states_need(post, problem):
        return post
    return None


def extract_need(post):
    try:
        formatted_extract_need_prompt = extract_need_prompt.format(
            title=post["title"],
            selftext=post["selftext"]
        )
        return curie_llm(formatted_extract_need_prompt).strip()
    except:
        return ""

def states_need(post, problem):
    question = f"Does this person have the following problem? {problem}"
    formatted_discern_applicability_prompt = discern_applicability_prompt.format(
        summary=post["summary"],
        question=question
    )
    # print(f"https://reddit.com{post['permalink']}")
    print(post["summary"])
    full_answer = davinci_llm(formatted_discern_applicability_prompt).strip()
    post["full_answer"] = full_answer
    # print()
    # print(post["summary"])
    # print()
    # print(full_answer)
    answer = full_answer.lower().split("answer:")[1].strip()
    # print(answer)
    return len(answer) >= 4 and answer[0:4] == "true"
