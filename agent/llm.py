import os

from langchain_aws import ChatBedrockConverse
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_openai import AzureChatOpenAI, ChatOpenAI


def get_chat_model() -> BaseChatModel:
    """Construct the configured LangChain chat model without invoking it."""
    provider = os.getenv("LLM_PROVIDER", "openai").strip().lower()

    if provider == "openai":
        return ChatOpenAI(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            temperature=0,
        )

    if provider == "azure_openai":
        deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")
        if not deployment:
            raise ValueError(
                "AZURE_OPENAI_DEPLOYMENT must be set when LLM_PROVIDER=azure_openai."
            )
        return AzureChatOpenAI(
            azure_deployment=deployment,
            api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview"),
            temperature=0,
        )

    if provider == "bedrock":
        return ChatBedrockConverse(
            model=os.getenv(
                "BEDROCK_MODEL_ID",
                "anthropic.claude-3-5-sonnet-20241022-v2:0",
            ),
            temperature=0,
        )

    raise ValueError(
        "LLM_PROVIDER must be one of: openai, azure_openai, bedrock."
    )
