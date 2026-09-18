from langchain_openai import ChatOpenAI
from langchain_huggingface import HuggingFaceHub,ChatHuggingFace
import os 
from dotenv import load_dotenv
from typing import Any

load_dotenv()

class ModelFactory:
    """
    Responsible for creating the language models instances
    """
    @staticmethod
    def create_model(
        model_name : str,
        temperature : float = 0.0,
        max_new_tokens : int = 512,
        api_key : str = None,
        huggingface_token : str | None = None
    ) -> Any:

       """
       create a huggingface chat model
       """ 
        
       token = (
        huggingface_token or os.getenv("HUGGINGFACEHUB_API_TOKEN")
       )
       
       if not token:
           raise ValueError(
               "HuggingFace API token is missing"
           )

       llm = HuggingFaceHub(
           repo_id = model_name,
           task = "text-generation",
           huggingfacehub_api_token=token,
           temperature=temperature,
           max_new_tokens=max_new_tokens,
       )

       chat_model = ChatHuggingFace(
           llm = llm
       )

       return chat_model
    