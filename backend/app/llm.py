import os
import re

from dotenv import load_dotenv
from groq import Groq


load_dotenv()

MODEL_NAME = "qwen/qwen3-32b"

client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
)


def clean_model_answer(answer: str) -> str:
    answer = re.sub(r"<think>.*?</think>", "", answer, flags=re.DOTALL)
    answer = answer.replace("\\n", "\n").replace('\\"', '"')
    return answer.strip()


def generate_answer(question: str, context: str, language: str = "auto") -> str:
    language_map = {
        "auto": (
            "Answer in the same language and writing style as the user's question. "
            "If the user writes in Roman script, answer in Roman script. "
            "If the user mixes languages, answer in the same mixed style."
        ),
        "english": "Answer in clear English.",
        "hindi": "Answer in Hindi using Devanagari script.",
        "hinglish": "Answer in Hinglish using Roman script.",
        "punjabi": "Answer in Punjabi using Gurmukhi script only.",
        "roman_punjabi": (
            "Answer in Roman Punjabi only. Do not use Gurmukhi script. "
            "Do not use Devanagari script. Use Latin letters like: "
            "'Deadlock oh situation hundi hai jithe processes ik duje di wait karde rehnde ne.'"
        ),
        "french": "Answer in French.",
        "spanish": "Answer in Spanish.",
    }

    language_instruction = language_map.get(language, language_map["auto"])

    prompt = f"""
Use the context below to answer the question.

Rules:
- Prioritize uploaded document context.
- Use web context only to improve explanation.
- Do not invent facts outside the context.
- Do not show reasoning steps.
- Do not output escaped strings.
- Do not include <think> tags.
- Give a clear answer in 4 to 7 sentences.
- {language_instruction}

Context:
{context}

Question:
{question}

Final answer:
"""

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a multilingual RAG assistant. "
                    "Return only the final answer. "
                    "Do not include thinking, reasoning steps, <think> tags, XML tags, or analysis."
                ),
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        temperature=0.2,
        max_completion_tokens=600,
    )

    answer = response.choices[0].message.content.strip()
    return clean_model_answer(answer)