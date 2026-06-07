"""Run a small offline demo using the in-memory KG and the existing LLM glue.

Usage:
    python scripts/run_demo.py

It will load `data/org_passages.csv`, ask for a question, retrieve matching
passages from the in-memory store, and call `llm.answer.generate_answer`.
"""
import os
import sys
# ensure project root is on sys.path for local imports
ROOT = os.path.dirname(os.path.dirname(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from kg.in_memory_kg import InMemoryKG

try:
    from llm.answer import generate_answer
except Exception:
    print('Could not import llm.answer. Ensure the project modules are on PYTHONPATH.')
    raise


def main():
    data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'org_passages.csv')
    if not os.path.exists(data_path):
        print('Data file not found at', data_path)
        sys.exit(1)

    kg = InMemoryKG()
    kg.bulk_load_csv(data_path, text_field='text')
    print(f'Loaded {len(kg.passages)} passages into in-memory KG.')

    demo_q = os.environ.get('DEMO_QUESTION')
    if demo_q:
        queries = [demo_q]
    else:
        queries = None

    while True:
        if queries is None:
            try:
                q = input('\nEnter a question (or blank to exit): ').strip()
            except (EOFError, KeyboardInterrupt):
                print('\nExiting demo.')
                return
            if not q:
                print('Exiting demo.')
                return
        else:
            q = queries.pop(0)

        # simple retrieval: search for keywords in question
        # choose top 5 passages that contain any token from question
        tokens = [t.strip().lower() for t in q.split() if t.strip()]
        candidates = []
        for p in kg.passages:
            score = 0
            txt = p['text'].lower()
            for tk in tokens:
                if tk and tk in txt:
                    score += 1
            if score > 0:
                candidates.append((score, p))

        candidates.sort(key=lambda x: -x[0])
        facts = [p['text'] for _, p in candidates[:8]]

        if not facts:
            print('No matching passages found — returning a fallback answer.')
            facts = ["No relevant facts found in local data."]

        print('\nGenerating answer from retrieved facts...')
        ans = generate_answer(q, facts)
        print('\nAnswer:\n')
        print(ans)

        if queries is not None and len(queries) == 0:
            print('\nDemo finished (DEMO_QUESTION used).')
            return


if __name__ == '__main__':
    main()
