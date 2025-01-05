import streamlit
from openai import OpenAI
import pandas as pd
from abstract_page import AbstractPage
from assistant import AssistantSettings, AssistantsDisplay, AssistantSettingsForm, ChatInterface

class AugmentedLLMPage(AbstractPage):
    def __init__(self):
        super().__init__(
            title="⚙️ The Augmented LLM",
            description="""> 'The basic building block of agentic systems is an LLM enhanced with augmentations such as retrieval, tools, and memory. Our current models can actively use these capabilities—generating their own search queries, selecting appropriate tools, and determining what information to retain.'""",
            initial_message_content="Hello! I am a tutor assistant that can help you understand your course material."
        )
        self.client = streamlit.session_state.client
        self.user_chat_message_content = None
        self.assistant_settings = AssistantSettings(
            AssistantSettingsForm.DEFAULT_ASSISTANT_ID,
            AssistantSettingsForm.DEFAULT_NAME,
            AssistantSettingsForm.DEFAULT_INSTRUCTIONS,
            None,
            AssistantSettingsForm.DEFAULT_MODEL
        )

        self.initialise_selected_assistant()

    def initialise_selected_assistant(self):
        if streamlit.session_state.selected_assistant is None:
            streamlit.session_state.selected_assistant = AssistantSettingsForm.DEFAULT_ASSISTANT_ID

    def display(self):
        self.display_title_and_description()
        self.display_tabs(["Chat", "Assistants", "Settings"])

    def display_tabs(self, tab_names):
        self.tabs = streamlit.tabs(tab_names)
        with self.tabs[0]:
            self.chat_interface = ChatInterface(assistant_id=streamlit.session_state.selected_assistant)
            self.user_chat_message_content = self.chat_interface.display()
        with self.tabs[1]:
            assistants_display = AssistantsDisplay()
            assistants_display.display()
        with self.tabs[2]:
            settings_form = AssistantSettingsForm()
            settings_form.display()


# Main Function
def main():
    page = AugmentedLLMPage()
    page.display()

if __name__ == "__main__":
    main()
