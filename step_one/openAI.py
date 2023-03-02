from langchain.prompts import PromptTemplate
from langchain.llms import OpenAI
from typing import List
import ray
import json


curie_llm = OpenAI(model_name="text-curie-001", temperature=0)
davinci_llm = OpenAI(model_name="text-davinci-003", temperature=0)

generate_user_group_prompt = PromptTemplate(
    input_variables=["problem"],
    template="""List 7 user groups who have the following problem and a short reason why they have it. Below the list, list the top 3 groups who have the problem the most in the following syntax: ["user group 1", "user group 2", "user group 3"], and mark the array with the label "3 most:".

Problem: {problem}

User groups:""",
)

def generate_user_groups(need) -> List[str]:
    formatted_generate_user_group_prompt = generate_user_group_prompt.format(problem=need)
    full_answer = davinci_llm(formatted_generate_user_group_prompt)

    print(full_answer)

    answer_chunks = full_answer.lower().split("3 most:")
    if len(answer_chunks) < 2:
        # If the answer is not formatted correctly, return None
        return None
    stripped_answer = answer_chunks[1].strip(' "\'\t\r\n')

    try:
        return json.loads(stripped_answer)
    except:
        return [stripped_answer, None, None]

restate_need_prompt = PromptTemplate(
    input_variables=["need"],
    template="""
State the following need concisely from the perspective of someone who has that need.

Need: {need}

Restated:
"""
)

def restate_need(need):
    formatted_restate_need_prompt = restate_need_prompt.format(need=need)
    return davinci_llm(formatted_restate_need_prompt).strip(' "\'\t\r\n')

extract_need_prompt = PromptTemplate(
    input_variables=["title", "selftext"],
    template="""Here is a reddit post I am interested in:

title: {title}

contents: {selftext}

Who is this person? What are they asking for?

Summary:""",
)

def extract_need(post):
    try:
        post_content = post["selftext"] or "No content"
        formatted_extract_need_prompt = extract_need_prompt.format(
            title=post["title"],
            selftext=post_content
        )
        return curie_llm(formatted_extract_need_prompt).strip()
    except:
        try:
            # If it failed because the post was too long, truncate it and try again.
            if len(post_content) > 2000:
                post_content = post_content[:2000]
                formatted_extract_need_prompt = extract_need_prompt.format(
                    title=post["title"],
                    selftext=post_content
                )
                return curie_llm(formatted_extract_need_prompt).strip()
        except:
            return None
    

discern_applicability_prompt = PromptTemplate(
    input_variables=["title", "summary", "need"],
    template="""
Here is the title and summary of a reddit post I am interested in:

title: {title}
summary: {summary}

Does the person writing this post have the following need themselves? {need}

Explain your reasoning before you answer, then answer \"true\" or \"false\" in a separate paragraph. Label your true/false answer with \"Answer:\".""" ,
)

def discern_applicability(post, need):
    formatted_discern_applicability_prompt = discern_applicability_prompt.format(
        title=post["title"],
        summary=post["summary"],
        need=need
    )
    full_answer = davinci_llm(formatted_discern_applicability_prompt).strip()
    post["full_answer"] = full_answer
    # print("\n\n")
    # print(f"https://reddit.com{post['permalink']}")
    # print(post["summary"])
    # print(formatted_discern_applicability_prompt)
    # print(full_answer)
    answer_chunks = full_answer.lower().split("answer:")
    if len(answer_chunks) < 2:
        # If the answer is not formatted correctly, return False
        return False
    answer = answer_chunks[1].strip()
    # print(answer)
    return len(answer) >= 4 and answer[0:4] == "true"

subreddit_is_relevant_prompt = PromptTemplate(
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
def subreddit_is_relevant(subreddit, need):
    formatted_subreddit_is_relevant_prompt = subreddit_is_relevant_prompt.format(
        subreddit=subreddit["name"],
        subreddit_description=subreddit["description"],
        need=need
    )
    full_answer = davinci_llm(formatted_subreddit_is_relevant_prompt).strip()
    print(subreddit["name"])
    print(subreddit["description"])
    print(full_answer)
    answer_relevance_string = full_answer.lower().split("answer:")[1].strip()
    print(answer_relevance_string)
    answer_relevance = 0
    try:
        answer_relevance = int(answer_relevance_string)
    except:
        pass
    subreddit["score"] = answer_relevance
    return subreddit