import os
from scripts.generate_org_chart_dataset import generate_passages, save_csv


def main():
    passages = generate_passages(1500)
    out_path = os.path.normpath(os.path.join(os.path.dirname(__file__), "data", "org_passages.csv"))
    save_csv(passages, out_path)
    print(f"Saved {len(passages)} passages to {out_path}")


if __name__ == "__main__":
    main()
