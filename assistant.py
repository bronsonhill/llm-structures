import streamlit as st
import time

class AssistantSettings():
    def __init__(self, id, name, instructions, vector_store, model):
        self.id = id
        self.name = name
        self.instructions = instructions
        self.vector_store = vector_store
        self.model = model
        
class AssistantsDisplay:
    def __init__(self):
        self.client = st.session_state.client

    def retrieve_assistants(self):
        assistants = self.client.beta.assistants.list(
            order="desc",
            limit=15
        )
        return assistants

    def display(self):
        assistants = self.retrieve_assistants()
        st.write("# Assistants")
        for assistant in assistants:
            self.display_assistant(assistant)

    def display_assistant(self, assistant):
        with st.container(border=True):
            st.header(f"{assistant.name}")
            readable_time = time.strftime('%Y-%m-%d %H:%M', time.localtime(assistant.created_at))
            st.caption(f"{assistant.id} created **{readable_time}**")
            st.subheader(f"Instructions:")
            st.write(f"#### {assistant.instructions}")
            st.write(f"**Model**: {assistant.model}")
            # st.write(f"**Tools**: {assistant.tools}")

            select_column, edit_column, spacer_column, delete_column = st.columns([1, 1, 3, 1])

            with select_column:
                st.button("Select", key=assistant.id + 'select', on_click=lambda a_id=assistant.id: self.select_assistant(a_id), type="secondary", icon="✅")
            with edit_column:
                st.button("Edit", key=assistant.id + 'edit', on_click=lambda a=assistant: self.edit_assistant(a), type="secondary", icon="✏️")
            with delete_column:
                st.button("Delete", key=assistant.id + 'delete', on_click=lambda a_id=assistant.id: self.delete_assistant(a_id), type="primary", icon="🗑️")

    def select_assistant(self, assistant_id):
        st.session_state["messages"] = []
        st.session_state.selected_assistant = assistant_id
        st.toast(f"Assistant {assistant_id} selected successfully.", icon="✅")   

    def edit_assistant(self, assistant):
        with st.form(key=f"edit_form_{assistant.id}"):
            new_name = st.text_input("Edit assistant name", value=assistant.name)
            new_instructions = st.text_area("Edit assistant instructions", value=assistant.instructions)
            new_model = st.radio("Edit assistant model", ["gpt-4o-mini", "gpt-4o"], index=["gpt-4o-mini", "gpt-4o"].index(assistant.model))
            submit_button = st.form_submit_button("Save Changes")

            if submit_button:
                self.client.beta.assistants.update(
                    assistant_id=assistant.id,
                    name=new_name,
                    instructions=new_instructions,
                    model=new_model
                )
                st.toast(f"Assistant {assistant.id} updated successfully.", icon="✏️")

    def delete_assistant(self, assistant_id):
        self.client.beta.assistants.delete(assistant_id=assistant_id)
        st.toast(f"Assistant {assistant_id} deleted successfully.", icon="🗑️")

class AssistantSettingsForm:
    DEFAULT_NAME = "University Socratic Tutor"
    DEFAULT_INSTRUCTIONS = "You are a socratic tutor for a university student. Help them understand the material."
    DEFAULT_MODEL = "gpt-4o-mini"
    DEFAULT_ASSISTANT_ID = "asst_pTXwNaRFg48IXBe3cw2exyv5"

    def __init__(self):
        self.client = st.session_state.client
        
    
    def display(self):
        st.write("# Create an assistant")
        with st.form(key="settings_form"):
            self.display_fields()
            uploaded_files = st.file_uploader("Upload file(s)", type=["txt", "md", "pdf"], accept_multiple_files=True)
            submit_button = st.form_submit_button("Submit", on_click= lambda f=uploaded_files: self.submit(f))

    def display_fields(self):
        self.name_field = st.text_input("Enter assistant name", self.DEFAULT_NAME)
        self.instructions_field = st.text_area("Enter assistant instructions", self.DEFAULT_INSTRUCTIONS)
        self.model_field = st.radio("Select model", ["gpt-4o-mini", "gpt-4o"], index=0)

    def submit(self, uploaded_files):
        # create assistant with client
        assistant = self.client.beta.assistants.create(
            name=self.name_field,
            instructions=self.instructions_field,
            model=self.model_field
        )

        if uploaded_files:
            # implement adding files (to a vector store?)
            self.create_vector_store(uploaded_files)
    
    def create_vector_store(self, uploaded_files):
        # create vector store with client
        vector_store = self.client.beta.vector_stores.create(
            name="Vector store for " + self.name_field,

        )

class ChatInterface:
    def __init__(self, assistant_id):
        self.client = st.session_state.client
        self.thread = self.initialise_thread()
        self.assistant = self.client.beta.assistants.retrieve(st.session_state.selected_assistant)
        self.chat_container = st.container()
        self.footer_container = st.container()

    def initialise_thread(self):
        if 'thread' in st.session_state and st.session_state.thread:
            return st.session_state.thread
        else:
            return self.create_thread()

    def create_thread(self):
        thread = self.client.beta.threads.create()
        st.session_state.thread = thread
        return thread

    def display(self):
        with self.chat_container:
            self.display_chat_messages()
        
        with self.footer_container:
            chat_input_placeholder = st.empty()
            user_chat_message_content = chat_input_placeholder.chat_input()

        if user_chat_message_content:
            self.handle_user_input(user_chat_message_content)

        return user_chat_message_content

    def display_chat_messages(self):
        if "messages" not in st.session_state:
            st.session_state["messages"] = []
        
        st.chat_message("assistant").write("Hello, there.")
        for message in st.session_state["messages"][1:]:
            if message["role"] == "user":
                st.chat_message("user").write(message["content"])
            elif message["role"] == "assistant":
                st.chat_message("assistant").write(message["content"])

    def handle_user_input(self, user_input):
        with self.chat_container:
            st.chat_message("user").markdown(user_input)
        self.add_user_message_to_session(user_input)
        self.add_user_message_to_thread(user_input)
        response = self.get_client_response()
        message = response.data[0].content[0].text.value
        with self.chat_container:
            st.chat_message("assistant").markdown(message)
        self.add_assistant_message_to_session(message)

    def add_user_message_to_session(self, content):
        st.session_state["messages"].append({"role": "user", "content": content})
    
    def add_assistant_message_to_session(self, content):
        st.session_state["messages"].append({"role": "assistant", "content": content})

    def add_user_message_to_thread(self, content):
        self.client.beta.threads.messages.create(
            thread_id=self.thread.id,
            role="user",
            content=content
        )

    def get_client_response(self):
        run = self.client.beta.threads.runs.create_and_poll(
            thread_id=self.thread.id,
            assistant_id=self.assistant.id,
        )
        if run.status == 'completed': 
            messages = self.client.beta.threads.messages.list(
                thread_id=self.thread.id
            )
            return messages
        else:
            print(run.status)