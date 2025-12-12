import os
from strands.models.openai import OpenAIModel

def get_model():
    """
    Returns a configured Model instance based on environment variables.
    Defaults to OpenAI-compatible provider.
    """
    api_key = os.getenv("LLM_API_KEY")
    base_url = os.getenv("LLM_BASE_URL")
    model_id = os.getenv("LLM_MODEL", "gpt-4o") # Default to gpt-4o if not set

    if not api_key:
        raise ValueError("LLM_API_KEY environment variable is not set.")

    client_args = {"api_key": api_key}
    if base_url:
        client_args["base_url"] = base_url

    return OpenAIModel(
        client_args=client_args,
        model_id=model_id,
        params={
            "temperature": 0.7,
        }
    )
