from __future__ import annotations

from typing import Any, Literal
from textwrap import dedent

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate

from ..core.config import Settings

try:
    from langchain_openai import ChatOpenAI
except ImportError:  # pragma: no cover
    ChatOpenAI = None

try:
    from langchain_google_genai import ChatGoogleGenerativeAI
except ImportError:  # pragma: no cover
    ChatGoogleGenerativeAI = None

try:
    from langchain_anthropic import ChatAnthropic
except ImportError:  # pragma: no cover
    ChatAnthropic = None


ProviderName = Literal["openai", "gemini", "anthropic", "local"]


class LLMService:
    """Generate answers using an injected LangChain chat model."""

    def __init__(self, llm: BaseChatModel | None, provider_name: ProviderName = "local") -> None:
        self.llm = llm
        self.provider_name = provider_name

        self.answer_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", "You are a helpful assistant that strictly answers using the provided context."),
                (
                    "human",
                    dedent(
                        """
                        Use the context to answer the user's question. If the answer is absent, say you do not know.

                        Context:
                        {context}

                        Question: {question}
                        """
                    ).strip(),
                ),
            ]
        )

        self.title_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", "You create short descriptive titles for chat sessions."),
                (
                    "human",
                    dedent(
                        """
                        You are an assistant that summarizes conversations. Provide a concise title (max 6 words) that describes the following context:

                        {context}
                        """
                    ).strip(),
                ),
            ]
        )

    def generate_answer(self, question: str, context: str) -> str:
        if not context.strip():
            return "I could not find any relevant documents for this question."

        if not self.llm:
            return dedent(
                f"""
                No live LLM credentials were detected, so this answer is generated locally.

                Question: {question}

                Context excerpts:
                {context}
                """
            ).strip()

        prompt_value = self.answer_prompt.format_prompt(context=context, question=question)
        response = self._extract_content(self.llm.invoke(prompt_value.to_messages()))
        if response:
            return response

        return dedent(
            f"""
            The configured LLM provider ({self.provider_name}) did not return content.
            """
        ).strip()

    def generate_title(self, context: str) -> str:
        if not self.llm:
            return "Chat session"

        prompt_value = self.title_prompt.format_prompt(context=context)
        response = self._extract_content(self.llm.invoke(prompt_value.to_messages()))
        if response:
            return response

        return "Chat session"

    @staticmethod
    def _extract_content(message: Any) -> str:
        """Return concatenated text content from LangChain chat responses."""
        if message is None:
            return ""

        content = getattr(message, "content", None)
        if isinstance(content, str):
            return content.strip()

        parts: list[str] = []
        if isinstance(content, list):
            for item in content:
                if isinstance(item, str) and item.strip():
                    parts.append(item.strip())
                elif isinstance(item, dict) and "text" in item:
                    text = str(item.get("text", "")).strip()
                    if text:
                        parts.append(text)
                else:
                    text = getattr(item, "text", None)
                    if text and str(text).strip():
                        parts.append(str(text).strip())

        return "\n".join(parts).strip()


def build_llm(settings: Settings) -> tuple[BaseChatModel | None, ProviderName]:
    """Select an LLM provider based on configuration (DI-friendly)."""
    provider = (settings.llm_provider or "auto").lower()

    if provider in ("auto", "openai"):
        model = _build_openai_llm(settings)
        if model:
            return model, "openai"
        if provider == "openai":
            return None, "local"

    if provider in ("auto", "gemini"):
        model = _build_gemini_llm(settings)
        if model:
            return model, "gemini"
        if provider == "gemini":
            return None, "local"

    if provider in ("auto", "anthropic"):
        model = _build_anthropic_llm(settings)
        if model:
            return model, "anthropic"
        if provider == "anthropic":
            return None, "local"

    return None, "local"


def _build_openai_llm(settings: Settings) -> BaseChatModel | None:
    if not (settings.openai_api_key and ChatOpenAI is not None):
        return None
    return ChatOpenAI(
        model=settings.chat_model,
        api_key=settings.openai_api_key,
        temperature=0.2,
    )


def _build_gemini_llm(settings: Settings) -> BaseChatModel | None:
    if not (settings.gemini_api_key and ChatGoogleGenerativeAI is not None):
        return None
    return ChatGoogleGenerativeAI(
        model=settings.gemini_chat_model,
        google_api_key=settings.gemini_api_key,
        temperature=0.2,
        convert_system_message_to_human=True,
    )


def _build_anthropic_llm(settings: Settings) -> BaseChatModel | None:
    if not (settings.anthropic_api_key and ChatAnthropic is not None):
        return None
    return ChatAnthropic(
        model=settings.anthropic_chat_model,
        api_key=settings.anthropic_api_key,
        temperature=0.2,
    )


def build_llm_service(settings: Settings) -> LLMService:
    llm, provider_name = build_llm(settings)
    return LLMService(llm=llm, provider_name=provider_name)
