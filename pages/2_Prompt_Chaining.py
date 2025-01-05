import streamlit as st
from abstract_page import AbstractPage
from assistant import ChatInterface


class PromptChainingPage(AbstractPage):
    def __init__(self):
        super().__init__(
            title="🔗 Prompt Chaining",
            description="""> 'Prompt chaining decomposes a task into a sequence of steps, where each LLM call processes the output of the previous one.'""",
            initial_message_content="Hello! I am a tutor assistant that can help you understand your course material."
        )
        self.client = st.session_state.client
        self.user_chat_message_content = None

    def display(self):
        self.display_title_and_description()
        self.display_tabs(["Construct", "Chat"])

    def display_tabs(self, tab_names):
        self.tabs = st.tabs(tab_names)
        with self.tabs[0]:
            st.write("This is the Construct tab")
        with self.tabs[1]:
            self.chat_interface = ChatInterface('asst_pTXwNaRFg48IXBe3cw2exyv5')
            self.user_chat_message_content = self.chat_interface.display()


# Main Function
def main():
    page = PromptChainingPage()
    page.display()

if __name__ == "__main__":
    main()