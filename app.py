import streamlit as st
from openai import OpenAI
import json
import os

DB_FILE = 'db.json'

def main():
    # Initialize OpenAI client using the secret-stored API key
    client = OpenAI(api_key=st.secrets["openai_api_key"])

    # List of models
    models = ["gpt-4o-mini", "gpt-4o", "gpt-4-turbo", "gpt-4", "gpt-3.5-turbo"]

    # Create a select box for the models
    st.session_state["openai_model"] = st.sidebar.selectbox("Select OpenAI model", models, index=0)

    # Load chat history from db.json
    with open(DB_FILE, 'r') as file:
        db = json.load(file)
    st.session_state.messages = db.get('chat_history', [])

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Accept user input
    if prompt := st.chat_input("What is up?"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)

        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            stream = client.chat.completions.create(
                model=st.session_state["openai_model"],
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ],
                stream=True,
            )
            response = st.write_stream(stream)
        st.session_state.messages.append({"role": "assistant", "content": response})

        # Store chat history to db.json
        db['chat_history'] = st.session_state.messages
        with open(DB_FILE, 'w') as file:
            json.dump(db, file)

    # Add a "Clear Chat" button to the sidebar
    if st.sidebar.button('Clear Chat'):
        # Clear chat history in db.json
        db['chat_history'] = []
        with open(DB_FILE, 'w') as file:
            json.dump(db, file)
        # Clear chat messages in session state
        st.session_state.messages = []
        st.rerun()

def login_page():
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    login_button = st.button("Login")

    # Authenticate using st.secrets for username and password
    if login_button:
        if username == st.secrets["username"] and password == st.secrets["password"]:
            st.session_state["authenticated"] = True
            st.success("Logged in successfully!")
            st.experimental_rerun()
        else:
            st.error("Invalid username or password")

if __name__ == '__main__':
    # Initialize chat history and authentication
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    # Create DB file if it does not exist
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, 'w') as file:
            db = {
                'openai_api_keys': [],
                'chat_history': []
            }
            json.dump(db, file)

    # Display login page or main app
    if st.session_state["authenticated"]:
        main()
    else:
        login_page()
