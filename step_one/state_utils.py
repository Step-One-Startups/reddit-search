import streamlit as st
import pandas as pd
import random


class UsageTracker:
    def __init__(self):
        print("tracker initialized")
        self.prompt_tokens = 0
        self.completion_tokens = 0

    def clear_usage(self):
        self.prompt_tokens = 0
        self.completion_tokens = 0

    def get_usage(self):
        return {
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
        }

    def add_tokens(self, prompt_tokens, completion_tokens):
        self.prompt_tokens += prompt_tokens
        self.completion_tokens += completion_tokens


def clear_usage():
    st.session_state.tracker.clear_usage()


def get_usage():
    return st.session_state.tracker.get_usage()


def add_tokens(prompt_tokens, completion_tokens):
    st.session_state.tracker.add_tokens(prompt_tokens, completion_tokens)


POSSIBLE_NEEDS = [
    "Forming new habits is hard",
    "Feeling unsafe walking alone",
    "GPT-4 is too expensive",
    "Finding users and determining if a startup problem is real",
    "Want to protect myself from government surveillance",
]

INITIAL_NEED = POSSIBLE_NEEDS[0]


def initialize_state():
    if "need" not in st.session_state:
        st.session_state["need"] = INITIAL_NEED

    if "num_scorable_posts" not in st.session_state:
        st.session_state.num_scorable_posts = 0

    if "scored_posts" not in st.session_state:
        st.session_state.scored_posts = pd.DataFrame({"link": [], "score": []})

    if "tracker" not in st.session_state:
        st.session_state.tracker = UsageTracker()


# Allow the user to quickly see responses for different needs
def randomize_need():
    st.session_state["need"] = POSSIBLE_NEEDS[
        random.randint(0, len(POSSIBLE_NEEDS) - 1)
    ]


def clear_recorded_scores():
    st.session_state.scored_posts = pd.DataFrame({"link": [], "score": []})


def record_score(link, score):
    print("st.session_state in record_store", st.session_state)
    index = len(st.session_state.scored_posts)
    st.session_state.scored_posts.loc[index] = [link, score]
