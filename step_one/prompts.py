from langchain.prompts import PromptTemplate

extract_need_prompt = PromptTemplate(
    input_variables=["title", "selftext"],
    template="""Here is a reddit post I am interested in:

title: {title}

contents: {selftext}

Summarize this post in a paragraph. Who is this person? What are they asking for?""",
)

discern_applicability_prompt = PromptTemplate(
    input_variables=["title", "summary", "question"],
    template="""
Here is the title and summary of a reddit post I am interested in:

title: {title}
summary: {summary}

Please answer the following question:

{question}

Explain your reasoning before you answer, then answer \"true\" or \"false\" in a separate paragraph. Label your true/false answer with \"Answer:\".""" ,
)

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