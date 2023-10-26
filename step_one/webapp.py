import streamlit as st
from step_one.find import find_posts
from step_one.state_utils import (
    initialize_state,
    randomize_need,
    clear_recorded_scores,
)
from step_one.calculate_cost import calculate_formatted_cost

initialize_state()

st.title("OpenPipe Reddit Search Demo")


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

posts, prompt_tokens, completion_tokens = get_posts(need)

data = [
    {"Metric": "Input tokens", "Value": prompt_tokens},
    {"Metric": "Output tokens", "Value": completion_tokens},
    {
        "Metric": "Total cost with GPT-4",
        "Value": calculate_formatted_cost("gpt_4", prompt_tokens, completion_tokens),
    },
    {
        "Metric": "Total cost with Mistral 7b",
        "Value": calculate_formatted_cost(
            "mistral_7b", prompt_tokens, completion_tokens
        ),
    },
]

st.subheader("Total Usage")
st.dataframe(data=data, use_container_width=True, hide_index=True)

st.header("Results")

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
    div[data-testid="stVerticalBlock"] div[data-testid="stVerticalBlock"] div[data-testid="stVerticalBlock"] {
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
