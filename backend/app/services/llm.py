from __future__ import annotations

from textwrap import dedent

from ..core.config import Settings

try:
    from openai import OpenAI
except ImportError:  # pragma: no cover
    OpenAI = None

try:
    import google.generativeai as genai
except ImportError:  # pragma: no cover
    genai = None


class LLMService:
    """Generate answers using OpenAI or a deterministic fallback."""

    def __init__(self, settings: Settings) -> None:
        self.openai_model = settings.chat_model
        self.openai_client = None
        self.gemini_model = None

        if settings.openai_api_key and OpenAI is not None:
            self.openai_client = OpenAI(api_key=settings.openai_api_key)

        if settings.gemini_api_key and genai is not None:
            genai.configure(api_key=settings.gemini_api_key)
            self.gemini_model = genai.GenerativeModel(settings.gemini_chat_model)

    def generate_answer(self, question: str, context: str) -> str:
        if not context.strip():
            return "I could not find any relevant documents for this question."

        if self.openai_client:
            response = self.openai_client.chat.completions.create(
                model=self.openai_model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that strictly answers using the provided context.",
                    },
                    {
                        "role": "user",
                        "content": dedent(
                            f"""
                            Use the context to answer the user's question. If the answer is absent, say you do not know.

                            Context:
                            {context}

                            Question: {question}
                            """
                        ).strip(),
                    },
                ],
                temperature=0.2,
            )
            return response.choices[0].message.content or "I could not draft an answer."

        if self.gemini_model:
            prompt = dedent(
                f"""
                You are a helpful assistant that strictly answers using the provided context. If the answer is absent,
                say you do not know.

                Context:
                {context}

                Question: {question}
                """
            ).strip()
            response = self.gemini_model.generate_content(prompt)
            text = getattr(response, "text", None)
            if not text:
                candidates = getattr(response, "candidates", []) or []
                for candidate in candidates:
                    content = getattr(candidate, "content", None)
                    parts = getattr(content, "parts", None) if content else None
                    if not parts:
                        continue
                    for part in parts:
                        part_text = getattr(part, "text", None)
                        if part_text:
                            text = part_text
                            break
                    if text:
                        break
            return text or "I could not draft an answer."

        return dedent(
            f"""
            No live LLM credentials were detected, so this answer is generated locally.

            Question: {question}

            Context excerpts:
            {context}
            """
        ).strip()

    def generate_title(self, context: str) -> str:
        prompt = dedent(
            f"""
            You are an assistant that summarizes conversations. Provide a concise title (max 6 words) that describes the following context:

            {context}
            """
        ).strip()

        if self.openai_client:
            response = self.openai_client.chat.completions.create(
                model=self.openai_model,
                messages=[
                    {
                        "role": "system",
                        "content": "You create short descriptive titles for chat sessions.",
                    },
                    {
                        "role": "user",
                        "content": prompt,
                    },
                ],
                temperature=0.2,
                max_tokens=32,
            )
            return response.choices[0].message.content.strip() or "Chat session"

        if self.gemini_model:
            response = self.gemini_model.generate_content(prompt)
            text = getattr(response, "text", None)
            if not text:
                for candidate in getattr(response, "candidates", []) or []:
                    content = getattr(candidate, "content", None)
                    for part in getattr(content, "parts", []) if content else []:
                        part_text = getattr(part, "text", None)
                        if part_text:
                            text = part_text
                            break
                    if text:
                        break
            return text or "Chat session"

        return "Chat session"
