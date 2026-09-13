from langchain_huggingface import HuggingFaceHub
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI

from langgraph.graph import StateGraph,START,END

model = ChatOpenAI(
    model = "openai-community/gpt2",
    temperature = 0
)

