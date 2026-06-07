import csv
import random
import os

COMPANIES = [
    "Apex Systems",
    "BrightCore Inc",
    "Creston Labs",
    "DynamoWorks",
    "Everleaf Solutions",
    "Foresight Global",
    "GigaMatrix",
    "Horizon Dynamics",
    "Ionix Corp",
    "Jupiter Holdings",
]

ROLES = [
    "Chief Executive Officer", "CEO", "Chief Technology Officer", "CTO", "Chief Financial Officer", "CFO",
    "Head of Engineering", "Head of Product", "VP of Sales", "VP of Marketing", "Director of HR",
    "Engineering Manager", "Senior Engineer", "Product Manager", "Sales Lead", "HR Specialist",
]

DEPARTMENTS = ["Engineering", "Product", "Sales", "Marketing", "Human Resources", "Finance", "Legal"]


def make_relation(emp, role, comp, manager=None, dept=None):
    parts = []
    parts.append(f"{emp} is the {role} at {comp}.")
    if manager:
        parts.append(f"{emp} reports to {manager}.")
    if dept:
        parts.append(f"{emp} works in the {dept} department.")
    return " ".join(parts)


def generate_passages(n=1500):
    passages = []
    first_names = ["Alex", "Jordan", "Taylor", "Morgan", "Casey", "Riley", "Jamie", "Cameron", "Dana", "Avery"]
    last_names = ["Smith", "Johnson", "Lee", "Patel", "Garcia", "Nguyen", "Brown", "Khan", "Martinez", "Davis"]

    for i in range(n):
        comp = random.choice(COMPANIES)
        dept = random.choice(DEPARTMENTS)
        role = random.choice(ROLES)
        emp = f"{random.choice(first_names)} {random.choice(last_names)}"
        # occasionally create manager relationships
        manager = None
        if random.random() < 0.4:
            manager = f"{random.choice(first_names)} {random.choice(last_names)}"
        p = make_relation(emp, role, comp, manager=manager, dept=dept)
        passages.append(p)

    return passages


def save_csv(passages, outpath):
    os.makedirs(os.path.dirname(outpath), exist_ok=True)
    with open(outpath, "w", newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=["text"])
        writer.writeheader()
        for p in passages:
            writer.writerow({"text": p})


if __name__ == '__main__':
    passages = generate_passages(1500)
    out = os.path.join(os.path.dirname(__file__), "..", "data", "org_passages.csv")
    out = os.path.normpath(out)
    save_csv(passages, out)
    print(f"Saved {len(passages)} passages to {out}")
