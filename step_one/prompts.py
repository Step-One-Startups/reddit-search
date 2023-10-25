from openpipe import openai
from typing import List
import ray
import json


def score_post_relevance(post, need):
    completion = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {
                "role": "system",
                "content": "You are a helpful AI assistant whose job is to determine whether the author of a reddit post is likely to buy a product built to address a specific need.Score the following post on a scale of 1 to 10, where 1 means the author is very unlikely to buy the product and 10 means the author is very likely to buy the product. If they are working on a product that addresses the need, give them a low score. If you aren't sure, give them a score of 1.",
            },
            {
                "role": "user",
                "content": f"Need: {need}\n\nTitle: {post['title']}\n\nBody: {post['selftext']}",
            },
        ],
        function_call={"name": "score_post"},
        functions=[
            {
                "name": "score_post",
                "description": "Score the post on a scale of 1 to 10, where 1 means the author is very unlikely to buy the product and 10 means the author is very likely to buy the product.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "explanation": {"type": "string"},
                        "score": {
                            "type": "number",
                        },
                    },
                    "required": [
                        "explanation",
                        "score",
                    ],
                },
            }
        ],
        openpipe={"tags": {"prompt_id": "score_post_relevance"}},
    )
    try:
        arguments = json.loads(completion.choices[0].message.function_call.arguments)
    except:
        print("exception occurred, and here is the completion")
        print(completion)
        raise Exception(
            "exception occurred while parsing score_post_relevance completion"
        )
    return arguments["explanation"], arguments["score"]


def summarize_post(post):
    completion = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {
                "role": "system",
                "content": "You are a helpful AI assistant who summarizes reddit posts. Your goal is to summarize the following post in a single paragraph, while including as much detail as possible. Return the summary.",
            },
            {
                "role": "user",
                "content": f"Title: {post['title']}\n\nBody: {post['selftext']}",
            },
        ],
    )

    try:
        summary = completion.choices[0].message.content
    except:
        print("exception occurred, and here is the completion")
        print(completion)
        raise Exception("exception occurred while parsing summarize_post completion")
    return summary
