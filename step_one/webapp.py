import streamlit as st
from step_one.find import find_posts
from step_one.state_utils import (
    initialize_state,
    randomize_need,
    clear_recorded_scores,
)

initialize_state()

st.title("Step One")


@st.cache_data
def get_posts(need):
    clear_recorded_scores()
    return find_posts(need, st.write)


need = st.text_input(
    "User problem",
    key="need",
    label_visibility="visible",
    placeholder="GPT-4 is too expensive",
)

randomize_need_button = st.button(
    "Randomize problem", on_click=randomize_need, type="secondary"
)

st.header("Results")

# Explain that we are generating the results if we haven't already
st.write("Searching reddit...")

posts = get_posts(need)

col = st.columns(1)

with col[0]:
    for post in posts:
        with st.container():
            st.subheader(post["title"])
            st.write(post["permalink"])
            st.subheader("Summary:")
            st.write(post["summary"])
            with st.expander("See full post"):
                st.write(post["selftext"])
            st.subheader("Relevance explanation:")
            st.write(post["explanation"])

st.markdown(
    """
<style>
    div[data-testid="column"] div[data-testid="stVerticalBlock"] div[style*="flex-direction: column;"] div[data-testid="stVerticalBlock"] {
        border: 2px solid #f0f0f0; 
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
