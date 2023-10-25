import random
from step_one.find import find_posts
import streamlit as st

POSSIBLE_NEEDS = [
    "GPT-4 is too expensive",
    "Finding users and determining if a startup problem is real",
    "Forming new habits is hard",
    "Want to protect oneself from government surveillance",
    "Feeling unsafe walking alone",
]

INITIAL_NEED = POSSIBLE_NEEDS[0]


# Allow the user to quickly see responses for different needs
def randomize_activity():
    st.session_state["need"] = POSSIBLE_NEEDS[
        random.randint(0, len(POSSIBLE_NEEDS) - 1)
    ]


if "need" not in st.session_state:
    st.session_state["need"] = INITIAL_NEED

st.title("Step One")


@st.cache_data
def get_posts(need):
    return find_posts(need, st.write)


need = st.text_input(
    "User problem", key="need", label_visibility="visible", placeholder=INITIAL_NEED
)

randomize_need_button = st.button(
    "Randomize need", on_click=randomize_activity, type="secondary"
)

st.header("Results")

# Explain that we are generating the results if we haven't already
st.write("Finding matching posts...")
posts = get_posts(need)

for post in posts:
    with st.container():
        st.subheader(post["title"])
        st.write(f"https://reddit.com{post['permalink']}")
        st.subheader("Summary:")
        st.write(post["summary"])
        with st.expander("See full post"):
            st.write(post["selftext"])
        st.subheader("Relevance explanation:")
        st.write(post["explanation"])

st.markdown(
    """
<style>
    div[data-testid="stVerticalBlock"] div[style*="flex-direction: column;"] div[data-testid="stVerticalBlock"] {
        border: 2px solid #f0f0f0; 
        background-color: #f8f8f8; 
        border-radius: 5px;
        padding: 20px;
        margin: 10px 0;
        word-break: break-word;
    }
    .element-container, .stMarkdown {
        max-width: 100%;
    }
</style>
""",
    unsafe_allow_html=True,
)
