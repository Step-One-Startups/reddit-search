import streamlit as st
import pandas as pd
import random
from dataclasses import dataclass
from typing import Any


POSSIBLE_NEEDS = [
    "GPT-4 is too expensive",
    "Finding users and determining if a startup problem is real",
    "Forming new habits is hard",
    "Want to protect oneself from government surveillance",
    "Feeling unsafe walking alone",
]

INITIAL_NEED = POSSIBLE_NEEDS[0]


def initialize_state():
    if "need" not in st.session_state:
        st.session_state["need"] = INITIAL_NEED

    if "num_scorable_posts" not in st.session_state:
        st.session_state.num_scorable_posts = 0

    if "scored_posts" not in st.session_state:
        st.session_state.scored_posts = pd.DataFrame({"link": [], "score": []})


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
