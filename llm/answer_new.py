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
    facts_text = "\n".join([str(f) for f in facts]) if facts else "No specific facts found."
    prompt = f"Question: {question}\n\nFacts: {facts_text}\n\nAnswer:"
    
    try:
        out = gen(prompt, max_length=120, do_sample=True, temperature=0.8)
        if out and isinstance(out, list) and len(out) > 0:
            generated = out[0].get("generated_text", "")
            if generated:
                answer = generated.replace(prompt, "").strip()
                if answer:
                    return answer
    except Exception as e:
        print(f"Generation error: {e}")
    
    return f"Based on available facts: {facts_text}"
