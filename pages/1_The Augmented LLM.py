import streamlit
from openai import OpenAI
import requests


client = OpenAI(api_key=streamlit.session_state["api_key"])


def initialise_assistant(client):
    return client.beta.assistants.create(
        name="University Socratic Tutor",
        instructions="You are a socratic tutor for a university student. Help them understand the material.",
        model="gpt-4o-mini",
        tools=[{"type": "file_search"}],
    )

def display_title_and_description():
    streamlit.title("⚙️ The Augmented LLM")
    streamlit.markdown(
        """> 'The basic building block of agentic systems is an LLM enhanced with augmentations such as retrieval, tools, and memory. Our current models can actively use these capabilities—generating their own search queries, selecting appropriate tools, and determining what information to retain.'"""
    )
    streamlit.write(" -- [Building effective agents](https://www.anthropic.com/research/building-effective-agents)")
    streamlit.write("---")

def initialize_session_state():
    if "messages" not in streamlit.session_state:
        streamlit.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]

def display_chat_messages():
    for msg in streamlit.session_state.messages:
        streamlit.chat_message(msg["role"]).write(msg["content"])

def sidebar_components():
    # add assistant creation
    
    with streamlit.sidebar:
        streamlit.write("# Create an assistant")
        streamlit.text_input("Enter assistant name", 'Socratic University Tutor')
        streamlit.text_area("Enter assistant instructions", 'You are a socratic tutor for a university student. Help them understand their material.')

        uploaded_file = streamlit.file_uploader("Upload a file", type=["txt", "md", "pdf"], accept_multiple_files=True)
        enable_function_call = streamlit.checkbox("Enable function calling")
    return uploaded_file, enable_function_call

def upload_file(files):
    vector_store = client.beta.vector_stores.create(name="Learning Materials")
    file_streams = [open(path, "rb") for path in files]

    file_batch = client.beta.vector_stores.file_batches.upload_and_poll(
        vector_store_id=vector_store.id, files=file_streams
    )

    print(file_batch.status)
    print(file_batch.file_counts)

    
    return

def handle_user_input(uploaded_files, enable_web_search):
    if prompt := streamlit.chat_input():
        streamlit.session_state.messages.append({"role": "user", "content": prompt})
        streamlit.chat_message("user").write(prompt)

        context = ""
        if uploaded_files:
            upload_file(uploaded_files)

        if context:
            streamlit.session_state.messages.append({"role": "system", "content": context})

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=streamlit.session_state.messages
        )
        msg = response.choices[0].message.content
        streamlit.session_state.messages.append({"role": "assistant", "content": msg})
        streamlit.chat_message("assistant").write(msg)

def main():
    display_title_and_description()
    initialize_session_state()
    display_chat_messages()
    uploaded_files, enable_function_call = sidebar_components()
    initialise_assistant(client)
    handle_user_input(uploaded_files, enable_function_call)

if __name__ == "__main__":
    main()