import time
from requests import HTTPError
from openpipe import openai
import json
import random


def score_post_relevance(post, need):
    num_tries = 0
    while num_tries < 5:
        try:
            completion = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful AI assistant whose job is to determine whether the author of a reddit post is likely to buy a product built to address a specific need.Score the following post on a scale of 1 to 3, where 1 means the author is very unlikely to buy the product and 3 means the author is almost certain to buy the product. If they are working on a product that addresses the need, give them a low score. If you aren't sure, give them a score of 1.",
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
                        "description": "Score the post on a scale of 1 to 3, where 1 means the author is very unlikely to buy the product and 3 means the author is very likely to buy the product.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "score": {
                                    "type": "number",
                                },
                            },
                            "required": [
                                "score",
                            ],
                        },
                    }
                ],
                openpipe={"tags": {"prompt_id": "score_post_relevance"}},
            )
            break  # exit loop if the call is successful
        except HTTPError as e:
            if e.response.status_code in [499, 502]:
                num_tries += 1
                # back off as num_tries increases
                time.sleep(num_tries**2 * (1 + random.random()))
            else:
                raise
    try:
        arguments = json.loads(completion.choices[0].message.function_call.arguments)
    except:
        print("exception occurred, and here is the completion")
        print(completion)
        raise Exception(
            "exception occurred while parsing score_post_relevance completion"
        )
    return arguments["score"], completion.usage


def explain_relevance(post, need):
    num_tries = 0
    while num_tries < 5:
        try:
            completion = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful AI assistant whose job is to explain why a reddit post is relevant to a specific need. Explain why the following post is relevant to the need in a single short paragraph.",
                    },
                    {
                        "role": "user",
                        "content": f"Need: {need}\n\nTitle: {post['title']}\n\nBody: {post['selftext']}",
                    },
                ],
                openpipe={"tags": {"prompt_id": "explain_relevance"}},
            )
            break  # exit loop if the call is successful

        except HTTPError as e:
            if e.response.status_code in [499, 502]:
                num_tries += 1
                # back off as num_tries increases
                time.sleep(num_tries**2 * (1 + random.random()))
            else:
                raise

    try:
        explanation = completion.choices[0].message.content
    except:
        print("exception occurred, and here is the completion")
        print(completion)
        raise Exception("exception occurred while parsing explain_relevance completion")

    return explanation, completion.usage


def summarize_reddit_post(post):
    num_tries = 0
    while num_tries < 5:
        try:
            completion = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful AI assistant who summarizes reddit posts. Your goal is to summarize the following post in a single short paragraph, while including as much detail as possible. Return the summary.",
                    },
                    {
                        "role": "user",
                        "content": f"Title: {post['title']}\n\nBody: {post['selftext']}",
                    },
                ],
                openpipe={"tags": {"prompt_id": "summarize_reddit_post"}},
            )
            break  # exit loop if the call is successful

        except HTTPError as e:
            if e.response.status_code in [499, 502]:
                num_tries += 1
                # back off as num_tries increases
                time.sleep(num_tries**2 * (1 + random.random()))
            else:
                raise

    try:
        summary = completion.choices[0].message.content
    except:
        print("exception occurred, and here is the completion")
        print(completion)
        raise Exception("exception occurred while parsing summarize_post completion")
    return summary, completion.usage
