import streamlit
from openai import OpenAI
import requests
from AbstractPage import AbstractPage
import time

class AugmentedLLMPage(AbstractPage):
    def __init__(self):
        super().__init__(
            title="⚙️ The Augmented LLM",
            description="""> 'The basic building block of agentic systems is an LLM enhanced with augmentations such as retrieval, tools, and memory. Our current models can actively use these capabilities—generating their own search queries, selecting appropriate tools, and determining what information to retain.'"""
        )
        self.client = self.initialize_client()

    def initialize_client(self):
        return OpenAI(api_key=streamlit.session_state["api_key"])

    def display_custom_fields(self):
        streamlit.write("# Create an assistant")
        streamlit.text_input("Enter assistant name", 'Socratic University Tutor')
        streamlit.text_area("Enter assistant instructions", 'You are a socratic tutor for a university student. Help them understand their material.')

    def sidebar_components(self):
        with streamlit.sidebar:
            self.display_custom_fields()
            uploaded_files = streamlit.file_uploader("Upload a file", type=["txt", "md", "pdf"], accept_multiple_files=True)
            enable_function_call = streamlit.checkbox("Enable function calling")
        return uploaded_files, enable_function_call


class Assistant:
    def __init__(self, client):
        self.client = client
        self.assistant = self.initialise_assistant()
        self.thread = client.beta.threads.create()
        self.vector_store = self.client.beta.vector_stores.create(name="Materials")

    def initialise_assistant(self):
        return self.client.beta.assistants.create(
            name="University Socratic Tutor",
            instructions="You are a socratic tutor for a university student. Help them understand the material.",
            model="gpt-4o-mini",
            tools=[{"type": "file_search"}],
        )

    def add_file_to_vector_store(self, files):
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
        # existing_file_ids = self.assistant.tool_resources.file_search
        existing_file_ids = []

        new_file_ids = existing_file_ids + self.add_files_direct_method(files)
        print(new_file_ids)
        self.assistant = self.client.beta.assistants.update(
            assistant_id=self.assistant.id,
            tool_resources={
                'file_search': {
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

    def handle_user_input(self, uploaded_files, enable_web_search):
        prompt = streamlit.chat_input()
        if not prompt:
            return
        self.add_user_message(prompt)
        if uploaded_files:
            self.add_file_to_vector_store(uploaded_files)
            self.associate_vector_store_with_assistant()
        response = self.get_openai_response()
        self.add_assistant_message(response)

    def add_user_message(self, prompt):
        streamlit.session_state.messages.append({"role": "user", "content": prompt})
        streamlit.chat_message("user").write(prompt)
        self.client.beta.threads.messages.create(
            thread_id=self.thread.id,
            role="user",
            content=prompt
        )

    def add_system_message(self, context):
        streamlit.session_state.messages.append({"role": "system", "content": context})
        self.client.beta.threads.messages.create(
            thread_id=self.thread.id,
            role="system",
            content=context
        )

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

    def add_assistant_message(self, response):
        content = response[0].text.value
        streamlit.session_state.messages.append({"role": "assistant", "content": content})
        streamlit.chat_message("assistant").write(content)
        self.client.beta.threads.messages.create(
            thread_id=self.thread.id,
            role="assistant",
            content=content
        )

# Main Function
def main():
    page = AugmentedLLMPage()
    assistant = Assistant(page.client)
    page.display_title_and_description()
    page.display_chat_messages()
    uploaded_files, enable_function_call = page.sidebar_components()
    assistant.handle_user_input(uploaded_files, enable_function_call)

if __name__ == "__main__":
    main()