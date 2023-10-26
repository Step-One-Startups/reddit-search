model_prices = {
    "gpt_4": {"prompt_token_price": 0.00003, "completion_token_price": 0.00006},
    "mistral_7b": {
        "prompt_token_price": 0.0000012,
        "completion_token_price": 0.0000016,
    },
}


def calculate_cost(model, prompt_tokens, completion_tokens):
    prices = model_prices[model]
    return (
        prompt_tokens * prices["prompt_token_price"]
        + completion_tokens * prices["completion_token_price"]
    )


def format_as_dollar(amount: float) -> str:
    """Format a number as a dollar amount with two decimal places."""
    return f"${amount:.3f}"


def calculate_formatted_cost(model, prompt_tokens, completion_tokens):
    return format_as_dollar(calculate_cost(model, prompt_tokens, completion_tokens))
