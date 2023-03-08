This repo contains a basic implementation of a reddit-searching tool built specifically to suit the needs of entrepreneurs who want to quickly find users who have a certain problem. This helps founders do two things:

1. Determine if a problem is real enough to build a company around solving.
2. Find initial users.

## Setting up

Setting up the project should be fairly painless if you're familiar with CLI commands.

1. `cd` into the root directory.
2. Create a `.env` file after the manner of the `.env.example` file and set your API token (skip if it's already set on your machine).
3. Run `poetry install` (If you don't have Poetry installed on your machine, you can install it [here](https://python-poetry.org/docs/#installation)).

## Running the CLI locally

From the root directory, run `poetry run step-one "An example problem that you have"`


## Running the WebApp locally

From the root directory, run `poetry run streamlit run ./webapp.py`