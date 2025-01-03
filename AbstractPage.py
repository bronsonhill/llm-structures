from abc import ABC, abstractmethod
import streamlit

class AbstractPage(ABC):
    def __init__(self, title, description):
        self.title = title
        self.description = description
        self.initialize_session_state()

    def initialize_session_state(self):
        if "messages" not in streamlit.session_state:
            streamlit.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]

    def display_title_and_description(self):
        streamlit.title(self.title)
        streamlit.markdown(self.description)
        streamlit.write("---")

    def display_chat_messages(self):
        for msg in streamlit.session_state.messages:
            streamlit.chat_message(msg["role"]).write(msg["content"])

    @abstractmethod
    def display_custom_fields(self):
        pass

    def add_sidebar_components(self, component):
        self.side_bar_components.append(component)

    