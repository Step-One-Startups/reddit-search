from langchain.prompts import PromptTemplate
from langchain.llms import OpenAI
import ray


curie_llm = OpenAI(model_name="text-curie-001", temperature=0)
davinci_llm = OpenAI(model_name="text-davinci-003", temperature=0)

restate_need_prompt = PromptTemplate(
    input_variables=["need"],
    template="""
State the following need as the simple title of a blog post from someone who has that problem.

Need: {need}

Title:
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

Does the person writing this post have the following problem themselves? {need}

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
    print("\n\n")
    print(f"https://reddit.com{post['permalink']}")
    print(post["summary"])
    # print(formatted_discern_applicability_prompt)
    print(full_answer)
    answer_chunks = full_answer.lower().split("answer:")
    if len(answer_chunks) < 2:
        # If the answer is not formatted correctly, return False
        return False
    answer = answer_chunks[1].strip()
    # print(answer)
    return len(answer) >= 4 and answer[0:4] == "true"

filter_subreddit_prompt = PromptTemplate(
    input_variables=["subreddit", "subreddit_description", "question"],
    template="""
Here is a subreddit I am interested in:
{subreddit}

Here is the description of the subreddit:
{subreddit_description}

Please answer the following question. If you are not sure, answer False:

{question}

Explain your reasoning before you answer, then answer \"true\" or \"false\" in a separate paragraph. Label your true/false answer with \"Answer:\".""" ,
)

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