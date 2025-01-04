import streamlit
import streamlit.components.v1 as components
from openai import OpenAI

streamlit.title("🏠 Home")
streamlit.caption("🚀 A collection of Streamlit apps powered by large language models (LLMs)")
streamlit.write(
    "Welcome to the Streamlit Large Language Model (LLM) agent examples! "
    "This collection of Streamlit apps demonstrates basic implementations of Anthropic's common agent patterns. "
    "It is based on the release [Building effective agents](https://www.anthropic.com/research/building-effective-agents)"
)
streamlit.write("---")




# iframe_src = "https://www.anthropic.com/research/building-effective-agents"
# components.iframe(iframe_src)


if "client" not in streamlit.session_state:
    api_key = streamlit.text_input("Enter your API Key", type="password")
    if api_key:
        streamlit.session_state["client"] = OpenAI(api_key=api_key)
else:
    streamlit.write("Your API key has been provided.")
    