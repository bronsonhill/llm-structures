import streamlit
from openai import OpenAI
import pandas as pd
import time
from abstract_page import AbstractPage
from assistant_settings import AssistantSettings

class AugmentedLLMPage(AbstractPage):
    def __init__(self):
        super().__init__(
            title="⚙️ The Augmented LLM",
            description="""> 'The basic building block of agentic systems is an LLM enhanced with augmentations such as retrieval, tools, and memory. Our current models can actively use these capabilities—generating their own search queries, selecting appropriate tools, and determining what information to retain.'""",
            initial_message_content="Hello! I am a tutor assistant that can help you understand your course material."
        )
        self.client = streamlit.session_state.client
        self.user_chat_message_content = None
        self.DEFAULT_NAME = "University Socratic Tutor"
        self.DEFAULT_INSTRUCTIONS = "You are a socratic tutor for a university student. Help them understand the material."
        self.DEFAULT_MODEL = "gpt-4o-mini"
        self.DEFAULT_ASSISTANT_ID = "asst_pTXwNaRFg48IXBe3cw2exyv5"
        self.assistant_settings = AssistantSettings(self.DEFAULT_ASSISTANT_ID, self.DEFAULT_NAME, self.DEFAULT_INSTRUCTIONS, [], self.DEFAULT_MODEL)
        self.assistants = self.retrieve_assistants()

    def display_settings_form(self):
        streamlit.write("# Create an assistant")
        with streamlit.form(key="settings_form"):
            self.display_settings_fields()
            uploaded_files = streamlit.file_uploader("Upload file(s)", type=["txt", "md", "pdf"], accept_multiple_files=True)
            enable_function_call = streamlit.checkbox("Enable function calling")
            submit_button = streamlit.form_submit_button("Submit", on_click=self.submit_settings_form)

        return uploaded_files, enable_function_call
    
    def submit_settings_form(self):
        pass
    
    def display_tabs(self, tab_names):
        self.tabs = streamlit.tabs(tab_names)
        with self.tabs[0]:
            self.chat_container = streamlit.container()
            with self.chat_container:
                self.display_chat_messages()
            chat_input_placeholder = streamlit.empty()
            self.user_chat_message_content = chat_input_placeholder.chat_input()
        with self.tabs[1]:
            self.display_assistants()
        with self.tabs[2]:
            self.display_settings_form()
            df = self.convert_assistants_to_df()
            self.display_assistants_in_df(df)
            
            
        return
    
    def retrieve_assistants(self):
        assistants = self.client.beta.assistants.list(
            order="desc",
            limit=15
        )
        return assistants.data
    
    def convert_assistants_to_df(self):
        data = []
        for assistant in self.assistants:
            data.append({
                "Name": assistant.name,
                "Instructions": assistant.instructions,
                "Model": assistant.model
                # "Tools": [tool for tool in assistant.tools]
            })
        return pd.DataFrame(data)
    
    def display_assistants_in_df(self, dataframe):
        streamlit.write("# Assistants")
        streamlit.dataframe(dataframe)

    def display_assistants(self):
        streamlit.write("# Assistants")
        for assistant in self.assistants:
            self.display_assistant(assistant)

    def display_assistant(self, assistant):
        with streamlit.container(border=True):
            streamlit.header(f"{assistant.name}")
            streamlit.caption(f"ID: {assistant.id}")
            streamlit.subheader(f"Instructions:")
            streamlit.write(f"#### {assistant.instructions}")
            streamlit.write(f"**Model**: {assistant.model}")
            streamlit.write(f"**Tools**: {assistant.tools}")


            select_column, edit_column, spacer_column, delete_column = streamlit.columns([1,1,3,1])

            with select_column:
                streamlit.button("Select", key=assistant.id+'select', on_click=lambda a_id=assistant.id: self.select_assistant, type="secondary", icon="✅")
            with edit_column:
                streamlit.button("Edit", key=assistant.id+'edit', on_click=lambda a=assistant: self.edit_assistant, type="secondary", icon="✏️")
            with delete_column:
                streamlit.button("Delete", key=assistant.id+'delete', on_click=lambda a_id=assistant.id: self.delete_assistant(a_id), type="primary", icon="🗑️")
            
    
    def select_assistant(self, assistant_id):
        self.assistant_settings.id = assistant_id
        streamlit.toast("Assistant selected successfully.", icon="✅")
        return

    def delete_assistant(self, assistant_id):
        self.client.beta.assistants.delete(assistant_id=assistant_id)
        self.assistants = self.retrieve_assistants()
        streamlit.toast("Assistant deleted successfully.", icon="🗑️")
        return
        

    @streamlit.dialog("Cast your vote")
    def edit_assistant(self, assistant):
        
        # with streamlit.form(key="edit_assistant_form"):
        streamlit.text_input("Enter assistant name", assistant.name)
        streamlit.text_area("Enter assistant instructions", assistant.instructions)
        streamlit.text_input("Enter assistant model", assistant.model)
            # submit_button = streamlit.form_submit_button("Submit", on_click=self.submit_edit_assistant_form)

    def submit_edit_assistant_form(self):
        pass


    def display_settings_fields(self):
        
        streamlit.text_input("Enter assistant name", self.DEFAULT_NAME)
        streamlit.text_area("Enter assistant instructions", self.DEFAULT_INSTRUCTIONS)

    def add_user_message(self, prompt):
        streamlit.session_state.messages.append({"role": "user", "content": prompt})
        with self.chat_container:
            streamlit.chat_message("user").write(prompt)

    def add_system_message(self, context):
        streamlit.session_state.messages.append({"role": "system", "content": context})
        with self.chat_container:
            streamlit.chat_message("system").write(context)

    def add_assistant_message(self, content):
        streamlit.session_state.messages.append({"role": "assistant", "content": content})
        with self.chat_container:
            streamlit.chat_message("assistant").write(content)


class Assistant:
    def __init__(self, settings: AssistantSettings):
        self.client = streamlit.session_state.client
        self.settings = settings
        self.assistant = self.initialise_assistant()
        self.thread = self.client.beta.threads.create()
        self.vector_store = None

    def initialise_assistant(self):
        if self.settings.id:
            return self.client.beta.assistants.retrieve(assistant_id=self.settings.id)
        
    def create_assistant(self):
        return self.client.beta.assistants.create(
            name=self.settings.name,
            instructions=self.settings.instructions,
            model=self.settings.model,
            tools=[{"type": "file_search"}],
        )
    
    def initialise_vector_store_if_none(self):
        if self.vector_store is None:
            self.vector_store = self.client.beta.vector_stores.create(name="Materials")

    def add_file_to_vector_store(self, files):
        self.initialise_vector_store_if_none()
        file_streams = [file for file in files]

        file_batch = self.client.beta.vector_stores.file_batches.upload_and_poll(
            vector_store_id=self.vector_store.id, 
            files=file_streams
        )

        print(file_batch.status)
        print(file_batch.file_counts)

    def associate_vector_store_with_assistant(self):
        self.assistant = self.client.beta.assistants.update(
            assistant_id=self.assistant.id,
            tool_resources={
                'file_search': {
                    'vector_store_ids': [self.vector_store.id]
                }
            }
        )

    def add_file_to_assistant(self, files):
        existing_file_ids = []
        new_file_ids = existing_file_ids + self.add_files_direct_method(files)
        print(new_file_ids)
        self.assistant = self.client.beta.assistants.update(
            assistant_id=self.assistant.id,
            tool_resources={
                'code_interpreter': {
                    'file_ids': new_file_ids
                }
            }
        )

    def add_files_direct_method(self, files) -> list:
        file_ids = []
        for file in files:
            response = self.client.files.create(
                file=file,
                purpose="assistants"
            )
            file_ids.append(response.id)
        return file_ids

    def handle_user_input(self, user_chat_message_content, page: AugmentedLLMPage):
        if not user_chat_message_content:
            return
        page.add_user_message(user_chat_message_content)
        self.client.beta.threads.messages.create(
            thread_id=self.thread.id,
            role="user",
            content=user_chat_message_content
        )
        response = self.get_openai_response()
        page.add_assistant_message(response[0].text.value)

    def get_openai_response(self):
        run = self.client.beta.threads.runs.create(
            thread_id=self.thread.id,
            assistant_id=self.assistant.id
        )
        while run.status in ["queued", "in_progress"]:
            run = self.client.beta.threads.runs.retrieve(thread_id=self.thread.id, run_id=run.id)
            time.sleep(0.5)
        messages = self.client.beta.threads.messages.list(thread_id=self.thread.id)
        return messages.data[0].content

# Main Function
def main():
    page = AugmentedLLMPage()
    assistant = Assistant(settings=page.assistant_settings)
    page.display_title_and_description()
    page.display_tabs(["Chat", "Assistants", "Settings"])
    assistant.handle_user_input(page.user_chat_message_content, page)

if __name__ == "__main__":
    main()