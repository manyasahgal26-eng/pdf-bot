import os
import re

from dotenv import load_dotenv
from groq import Groq


load_dotenv()

MODEL_NAME = "llama-3.3-70b-versatile"

client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
)


def clean_model_answer(answer: str) -> str:
    if not answer:
        return ""

    answer = re.sub(r"<think>.*?</think>", "", answer, flags=re.DOTALL)
    answer = answer.replace("\\n", "\n").replace('\\"', '"')
    answer = answer.strip()

    # If the model accidentally copies our context labels, keep only the
    # generated explanation after the leaked source marker.
    source_leak = re.search(r"Document source \d+:[^\n]*\n", answer)
    if source_leak:
        answer = answer[source_leak.end():].strip()

    doc_tag_leak = re.search(r"\[DOC \d+ \|[^\]]+\]\n", answer)
    if doc_tag_leak:
        answer = answer[doc_tag_leak.end():].strip()

    answer = re.sub(r"^Uploaded document context:\s*", "", answer, flags=re.IGNORECASE)
    answer = re.sub(r"^Web context:\s*", "", answer, flags=re.IGNORECASE)
    answer = re.sub(r"^Context:\s*", "", answer, flags=re.IGNORECASE)

    if answer.lower() in ["none", "null", "n/a"]:
        return ""

    return answer


def language_instruction_for(language: str) -> str:
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
            "Do not use Devanagari script. Use Latin letters."
        ),
        "french": "Answer in French.",
        "spanish": "Answer in Spanish.",
    }

    return language_map.get(language, language_map["auto"])


def generate_answer(question: str, context: str, language: str = "english") -> str:
    prompt = f"""
You are a precise document question-answering assistant.

Answer the user's exact question using the context below.

Rules:
- Give the answer directly. Do not explain what you are doing.
- If the context contains the answer, use it.
- If web context is present, use it only as supporting information.
- Do not copy long chunks from the context.
- Never output context labels such as "Uploaded document context", "Web context", or "Document source".
- Do not include prompt text, labels like "Question:", or internal reasoning.
- If the context is not enough, say exactly: I could not find this in the uploaded document or reliable web sources.
- Give a useful answer in 4 to 8 sentences.
- {language_instruction_for(language)}

User question:
{question}

Context:
{context}

Final answer:
"""

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a multilingual RAG assistant. Return only the final answer. "
                    "No reasoning, no XML tags, no markdown table, no prompt labels."
                ),
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        temperature=0.1,
        max_completion_tokens=700,
    )

    answer = clean_model_answer(response.choices[0].message.content)

    if not answer:
        return "I could not find this in the uploaded document or reliable web sources."

    return answer


def rewrite_query_for_search(question: str) -> str:
    prompt = f"""
Rewrite the user question into a clean search query for retrieving relevant document chunks.

Rules:
- Fix obvious spelling mistakes.
- Keep important technical terms.
- If the question is Hindi, Hinglish, Punjabi, French, or Spanish, translate it into clear English for search.
- Do not answer the question.
- Return only the search query.

User question:
{question}

Search query:
"""

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {
                "role": "system",
                "content": "You rewrite noisy questions into concise retrieval queries.",
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        temperature=0,
        max_completion_tokens=80,
    )

    rewritten = clean_model_answer(response.choices[0].message.content)

    if not rewritten:
        return question

    return rewritten


def classify_query(question: str) -> str:
    prompt = f"""
Classify the user's question into one of three categories:
1. 'document_retrieval': The question asks for facts, details, schedule, projects, or terms from the uploaded document (e.g., specific plans, dates, names, or content of a resume/roadmap/report).
2. 'web_search': The question asks about general real-world facts, current events, web-based info, or external information not likely contained in a personal or specific uploaded document (e.g., weather, public figures, news, general science, capital of a country).
3. 'computation': The question involves mathematical calculations, arithmetic, formulas, unit conversions, or logic problems (e.g., counting days, multiplying numbers, calculating rates, math equations).

Rules:
- Respond with exactly one word: 'document_retrieval', 'web_search', or 'computation'.
- Do not output any other text or explanation.

Question: {question}
Category:
"""
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {
                "role": "system",
                "content": "You are a precise classifier. Return only the class name: 'document_retrieval', 'web_search', or 'computation'. No reasoning, no markdown, no other words.",
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        temperature=0.0,
        max_completion_tokens=10,
    )
    decision = response.choices[0].message.content.strip().lower()
    if "web" in decision:
        return "web_search"
    if "computation" in decision or "compute" in decision or "math" in decision:
        return "computation"
    return "document_retrieval"


def generate_computation_answer(question: str) -> str:
    prompt = f"""
You are a precise mathematical and logical reasoning assistant.

Solve the user's question step-by-step and provide the final answer clearly.

Rules:
- Solve the math/logic problem accurately.
- Keep the final response short and directly to the point (within 3-5 sentences).
- Do not reference any external document or say you searched.

User Question:
{question}

Final Answer:
"""
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {
                "role": "system",
                "content": "You solve math and logic problems. Return only the step-by-step solution and final answer.",
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        temperature=0.1,
        max_completion_tokens=500,
    )
    return clean_model_answer(response.choices[0].message.content)


def generate_web_answer(question: str, context: str, language: str = "english") -> str:
    prompt = f"""
You are a precise assistant answering questions using web search results.

Answer the user's exact question using the web context below.

Rules:
- Give the answer directly. Do not explain what you are doing.
- Use the web context to construct a factual, accurate answer.
- Never output context labels such as "Web context" or "Document source".
- Do not include prompt text or internal reasoning.
- Give a useful answer in 4 to 8 sentences.
- {language_instruction_for(language)}

User question:
{question}

Web Context:
{context}

Final answer:
"""
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {
                "role": "system",
                "content": "You are a web question-answering assistant. Return only the final answer.",
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        temperature=0.2,
        max_completion_tokens=700,
    )
    return clean_model_answer(response.choices[0].message.content)

