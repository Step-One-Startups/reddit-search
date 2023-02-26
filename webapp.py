import random
from step_one.find import find_posts
import streamlit as st

POSSIBLE_NEEDS = [
    "Develop new habits.",
    "Protect oneself from government surveillance.",
    "Feeling unsafe walking alone",
    "Feeling lonely in the cafeteria"
]

INITIAL_NEED = POSSIBLE_NEEDS[0]

# Allow the user to quickly see responses for different needs
def randomize_activity():
    st.session_state['need'] = POSSIBLE_NEEDS[random.randint(0, len(POSSIBLE_NEEDS) - 1)]

if 'need' not in st.session_state:
    st.session_state['need'] = INITIAL_NEED

st.title('Step One')

@st.cache_data
def get_posts(need):
    return find_posts(need)


need = st.text_input("User problem", key="need", label_visibility="visible")

randomize_need_button = st.button("Randomize need", on_click=randomize_activity, type="secondary")

st.header('Results')

with st.empty():
    # Explain that we are generating the results if we haven't already
    st.write('Finding matching posts...')
    posts = get_posts(need)
    st.write(f'Found {len(posts)} matching posts:')


for post in posts:
    with st.container():
        st.subheader(post["title"])
        st.write(f"https://reddit.com{post['permalink']}")
        st.write(post["summary"])
        st.write("\n\n\n\n")