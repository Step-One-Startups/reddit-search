from langchain.prompts import PromptTemplate

extract_need_prompt = PromptTemplate(
    input_variables=["title", "selftext"],
    template="""Here is a reddit post I am interested in:

title: {title}

contents: {selftext}

What is this person asking for? Explain your reasoning in 5 sentences.""",
)

discern_applicability_prompt = PromptTemplate(
    input_variables=["summary", "question"],
    template="""
Here is a summary of a reddit post I am interested in:

{summary}

Please answer the following question. If you are not sure, answer False:

{question}

Explain your reasoning before you answer, then answer \"true\" or \"false\" in a separate paragraph. Label your true/false answer with \"Answer:\".""" ,
)