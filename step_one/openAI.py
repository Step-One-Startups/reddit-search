from langchain.prompts import PromptTemplate
from openpipe import openai
from typing import List
import ray
import json
import os
import requests
import string

def call_chatgpt(prompt_messages: List[str], model = "gpt-3.5-turbo"):
    messages = [{"role": "user", "content": message} for message in prompt_messages]
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=0,
    )
    try:
        return response.choices[0].message.content
    except:
        print("Error: ", response)
        return None

generate_user_group_prompt = PromptTemplate(
    input_variables=["problem"],
    template="""List 7 user groups who have the following problem on reddit. Below the list, name the top 3 groups who have the problem the most in the following syntax: ["user group 1", "user group 2", "user group 3"], and mark the array with the label "3 most:".

Problem: {problem}

User groups:""",
)

def generate_user_groups(need) -> List[str]:
    formatted_generate_user_group_prompt = generate_user_group_prompt.format(problem=need)
    full_answer = call_chatgpt(["You are a helpful AI assistant.", formatted_generate_user_group_prompt], model="gpt-4")

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
    

score_post_relevance_prompt = PromptTemplate(
    input_variables=["title", "selftext", "need"],
    template="""
Here is the title and body of a reddit post I am interested in:

title: {title}
body: {selftext}

On a scale of 1 to 10, how likely is it that the person writing this post has the following need? If you are not sure, make your best guess, or answer 1.

Need: {need}

Explain your reasoning before you answer, then answer one integer between 1 and 10 in a separate paragraph. Label your integer answer with \"Answer:\".""" ,
)

def score_post_relevance(post, need):
    formatted_score_post_relevance_prompt = score_post_relevance_prompt.format(
        title=post["title"],
        selftext=post["selftext"],
        need=need
    )
    try:
        full_answer = call_chatgpt(["You are a helpful AI assistant.", formatted_score_post_relevance_prompt], model="gpt-3.5-turbo-16k").strip()
        post["full_answer"] = full_answer
    except:
        print("\n\n")
        print("formatted_score_post_relevance_prompt", formatted_score_post_relevance_prompt)
        return 1

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
    full_answer = call_chatgpt(["You are a helpful AI assistant.", formatted_score_subreddit_relevance_prompt], model="gpt-3.5-turbo-16k").strip()
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