from langchain.prompts import PromptTemplate
from langchain.llms import OpenAI
from typing import List
import ray
import json
import os
import requests
import string

def call_chatgpt(prompt_messages: List[str]):
    messages = [{"role": "user", "content": message} for message in prompt_messages]
    data = {"model": "gpt-3.5-turbo", "messages": messages, "temperature": 0}
    headers = {"Authorization": "Bearer " + os.environ["OPENAI_API_KEY"], "Content-Type": "application/json"}
    response = requests.post("https://api.openai.com/v1/chat/completions", data=json.dumps(data), headers=headers)
    try:
        return response.json()["choices"][0]["message"]["content"]
    except:
        print("Error: ", response.json())
        return None


curie_llm = OpenAI(model_name="text-curie-001", temperature=0)
davinci_llm = OpenAI(model_name="text-davinci-003", temperature=0)

generate_user_group_prompt = PromptTemplate(
    input_variables=["problem"],
    template="""List 7 user groups who have the following problem and a short reason why they have it. Below the list, list the top 3 groups who have the problem the most in the following syntax: ["user group 1", "user group 2", "user group 3"], and mark the array with the label "3 most:".

Problem: {problem}

User groups:""",
)

restate_need_prompt = PromptTemplate(
    input_variables=["need"],
    template="""
Pretend you have the following need. State that need concisely in a single sentence from your perspective. The first word should be "I".

Need: {need}

Restated:
"""
)

def restate_need(need):
    formatted_restate_need_prompt = restate_need_prompt.format(need=need)
    full_answer = call_chatgpt(["You are a helpful AI assistant.", formatted_restate_need_prompt])
    return full_answer.strip(' "\'\t\r\n')

def generate_user_groups(need) -> List[str]:
    formatted_generate_user_group_prompt = generate_user_group_prompt.format(problem=need)
    full_answer = call_chatgpt(["You are a helpful AI assistant.", formatted_generate_user_group_prompt])

    print(full_answer)

    answer_chunks = full_answer.lower().split("3 most:")
    if len(answer_chunks) < 2:
        # If the answer is not formatted correctly, return empty array
        return []
    stripped_answer = answer_chunks[1].strip(' "\'\t\r\n')

    try:
        return json.loads(stripped_answer)
    except:
        return [stripped_answer, None, None]

summarize_post_prompt = PromptTemplate(
    input_variables=["title", "selftext", "need"],
    template="""Here is a reddit post I am interested in:

title: {title}

contents: {selftext}

Who is this person? What are they asking for? How does this post relate to the following need?

Need: {need}

Summary:""",
)

def summarize(post, need):
    try:
        post_content = post["selftext"] or "No content"
        formatted_summarize_post_prompt = summarize_post_prompt.format(
            title=post["title"],
            selftext=post_content,
            need=need
        )
        return call_chatgpt(["You are a helpful AI assistant.", formatted_summarize_post_prompt]).strip()
    except:
        try:
            # If it failed because the post was too long, truncate it and try again.
            if len(post_content) > 4000:
                post_content = post_content[:4000]
                formatted_summarize_post_prompt = summarize_post_prompt.format(
                    title=post["title"],
                    selftext=post_content
                )
                return call_chatgpt(["You are a helpful AI assistant.", formatted_summarize_post_prompt]).strip()
        except:
            return None
    

discern_applicability_prompt = PromptTemplate(
    input_variables=["title", "content", "need"],
    template="""
Here is the title and content of a reddit post I am interested in:

title: {title}
content: {content}

Does the person writing this post explicitly mention that they themselves have the following need? Answer \"true\" if they mention they have the following need or \"false\" if they don't.

Need: {need}

Explain your reasoning after the \"Reasoning\" label, then answer when you are done. Label your true/false answer with \"Answer:\" in a separate paragraph.

Reasoning:""",
)

def discern_applicability(post, need):
    # Truncate the post content to the last 1000 characters to save on tokens
    post_content = post["selftext"][-4000:] or "No content"
    print("character count", len(post["selftext"]))
    formatted_discern_applicability_prompt = discern_applicability_prompt.format(
        title=post["title"],
        content=post_content,
        need=need
    )
    full_answer = call_chatgpt(["You are a helpful AI assistant.", formatted_discern_applicability_prompt])

    if full_answer is None:
        return False

    post["full_answer"] = full_answer.strip()
    answer_chunks = full_answer.lower().split("answer:")
    if len(answer_chunks) < 2:
        # If the answer is not formatted correctly, return False
        return False
    answer = answer_chunks[1].strip()
    return len(answer) >= 4 and answer[0:4] == "true"

score_post_relevance_prompt = PromptTemplate(
    input_variables=["title", "summary", "need"],
    template="""
Here is the title and summary of a reddit post I am interested in:

title: {title}
summary: {summary}

On a scale of 1 to 10, how likely is it that the person writing this post has the following need? If you are not sure, make your best guess, or answer 1.

Need: {need}

Explain your reasoning before you answer, then answer one integer between 1 and 10 in a separate paragraph. Label your integer answer with \"Answer:\".""" ,
)

def score_post_relevance(post, need):
    formatted_score_post_relevance_prompt = score_post_relevance_prompt.format(
        title=post["title"],
        summary=post["summary"],
        need=need
    )
    full_answer = call_chatgpt(["You are a helpful AI assistant.", formatted_score_post_relevance_prompt]).strip()
    
    try:
        answer_relevance_string = full_answer.lower().split("answer:")[1].strip().translate(str.maketrans('', '', string.punctuation))
    except:
        print("\n\n")
        print("full_answer", full_answer)
        return 1
    answer_relevance = 1
    try:
        answer_relevance = int(answer_relevance_string)
    except:
        print("\n\n")
        print(f"answer_relevance_string `{answer_relevance_string}`")
        return 1
    print("answer_relevance", answer_relevance)
    return answer_relevance

score_subreddit_relevance_prompt = PromptTemplate(
    input_variables=["subreddit", "subreddit_description", "need"],
    template="""
Here is a subreddit I am interested in:
{subreddit}

Here is the description of the subreddit:
{subreddit_description}

Please answer the following question. If you are not sure, answer 1:

On a scale of 1 to 10, how likely is it than anyone in this subreddit has the following need? {need}

Explain your reasoning before you answer, then answer one integer between 1 and 10 in a separate paragraph. Label your integer answer with \"Answer:\".""" ,
)

@ray.remote
def score_subreddit_relevance(subreddit, need):
    formatted_score_subreddit_relevance_prompt = score_subreddit_relevance_prompt.format(
        subreddit=subreddit["name"],
        subreddit_description=subreddit["description"],
        need=need
    )
    full_answer = call_chatgpt(["You are a helpful AI assistant.", formatted_score_subreddit_relevance_prompt]).strip()
    print(subreddit["name"])
    print(subreddit["description"])
    print(full_answer)
    try:
        answer_relevance_string = full_answer.lower().split("answer:")[1].strip().translate(str.maketrans('', '', string.punctuation))
    except:
        print("\n\n")
        print("full_answer", full_answer)
        subreddit["score"] = 1
        return subreddit
    print(answer_relevance_string)
    answer_relevance = 0
    try:
        answer_relevance = int(answer_relevance_string)
    except:
        pass
    subreddit["score"] = answer_relevance
    return subreddit