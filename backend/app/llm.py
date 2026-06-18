from transformers import AutoModelForSeq2SeqLM, AutoTokenizer


MODEL_NAME = "google/flan-t5-base"

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)


def generate_answer(question: str, context: str) -> str:
    prompt = f"""
You are a helpful document assistant.

Use only the context below to answer the question.
Do not use outside knowledge.
If the context does not contain the answer, say:
I could not find this in the uploaded document.

Give a clear 2-4 sentence answer.

Context:
{context}

Question:
{question}

Answer:
"""

    inputs = tokenizer(
        prompt,
        return_tensors="pt",
        truncation=True,
        max_length=1024,
    )

    outputs = model.generate(
        **inputs,
        max_new_tokens=200,
        do_sample=False,
    )

    answer = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return answer.strip()