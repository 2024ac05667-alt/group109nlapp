from transformers import pipeline
import os


_gen = None


def _get_generator():
    global _gen
    if _gen is None:
        model_name = os.environ.get("QA_GEN_MODEL", "gpt2")
        _gen = pipeline("text-generation", model=model_name, device=-1)
    return _gen


def generate_answer(question: str, facts: list):
    gen = _get_generator()
    facts_text = "\n".join([str(f) for f in facts]) if facts else "No facts retrieved."
    prompt = (
        f"Use the facts below to answer the question concisely.\n\n"
        f"Facts:\n{facts_text}\n\nQuestion: {question}\nAnswer:"
    )
    out = gen(prompt, max_length=128, do_sample=False)
    return out[0]["generated_text"].strip()
