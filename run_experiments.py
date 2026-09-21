import json
import os
import subprocess
import tempfile
from pathlib import Path

from openai import OpenAI


# -----------------------------
# Configuration
# -----------------------------

MODEL = "gpt-4o-mini"

BASE_DIR = Path(__file__).parent
DOCS_DIR = BASE_DIR / "docs"
TESTS_FILE = BASE_DIR / "tests" / "test_cases.json"
RESULTS_DIR = BASE_DIR / "results"
RESULTS_FILE = RESULTS_DIR / "results.json"


client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])


# -----------------------------
# Load test cases
# -----------------------------

with open(TESTS_FILE, "r", encoding="utf-8") as f:
    test_cases = json.load(f)


# -----------------------------
# Documentation retrieval
# -----------------------------

def retrieve_documentation(concept):
    """
    Minimal documentation retrieval.

    Later this can be replaced with:
    - keyword search
    - BM25
    - embeddings
    - vector database
    """

    doc_file = DOCS_DIR / f"{concept}.txt"

    if not doc_file.exists():
        return ""

    return doc_file.read_text(encoding="utf-8")


# -----------------------------
# Ask LLM
# -----------------------------

def generate_proof(problem, documentation=None):

    if documentation:
        prompt = f"""
You are a Lean 4 proof assistant.

Solve the following problem by generating valid Lean 4 code.

Problem:
{problem}

Relevant Lean documentation:
{documentation}

Rules:
- Return ONLY Lean 4 code.
- Do not use Markdown.
- Do not explain the answer.
- Do not use sorry.
- Make the theorem self-contained.
"""
    else:
        prompt = f"""
You are a Lean 4 proof assistant.

Solve the following problem by generating valid Lean 4 code.

Problem:
{problem}

Rules:
- Return ONLY Lean 4 code.
- Do not use Markdown.
- Do not explain the answer.
- Do not use sorry.
- Make the theorem self-contained.
"""

    response = client.responses.create(
        model=MODEL,
        input=prompt
    )

    return response.output_text.strip()


# -----------------------------
# Run Lean
# -----------------------------

def verify_with_lean(code):

    with tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".lean",
        delete=False,
        encoding="utf-8"
    ) as f:

        f.write(code)
        file_path = f.name

    try:

        result = subprocess.run(
            ["lean", file_path],
            capture_output=True,
            text=True
        )

        return {
            "passed": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr
        }

    finally:

        os.remove(file_path)


# -----------------------------
# Run one experiment
# -----------------------------

def run_test(test):

    print("\n" + "=" * 60)
    print(f"TEST {test['id']}: {test['concept']}")
    print("=" * 60)

    problem = test["problem"]

    # -------------------------
    # WITHOUT DOCUMENTATION
    # -------------------------

    print("\n[1] Generating proof WITHOUT documentation...")

    proof_without_docs = generate_proof(problem)

    print("\nGenerated proof:")
    print(proof_without_docs)

    verification_without_docs = verify_with_lean(
        proof_without_docs
    )

    print(
        "\nLean result:",
        "PASS" if verification_without_docs["passed"]
        else "FAIL"
    )

    # -------------------------
    # WITH DOCUMENTATION
    # -------------------------

    documentation = retrieve_documentation(
        test["concept"]
    )

    print("\n[2] Retrieved documentation:")
    print(documentation)

    print("\nGenerating proof WITH documentation...")

    proof_with_docs = generate_proof(
        problem,
        documentation
    )

    print("\nGenerated proof:")
    print(proof_with_docs)

    verification_with_docs = verify_with_lean(
        proof_with_docs
    )

    print(
        "\nLean result:",
        "PASS" if verification_with_docs["passed"]
        else "FAIL"
    )

    # -------------------------
    # Store result
    # -------------------------

    return {
        "id": test["id"],
        "concept": test["concept"],
        "problem": problem,

        "without_documentation": {
            "proof": proof_without_docs,
            "passed": verification_without_docs["passed"],
            "error": verification_without_docs["stderr"]
        },

        "with_documentation": {
            "proof": proof_with_docs,
            "passed": verification_with_docs["passed"],
            "error": verification_with_docs["stderr"]
        }
    }


# -----------------------------
# Main
# -----------------------------

def main():

    RESULTS_DIR.mkdir(exist_ok=True)

    results = []

    for test in test_cases:

        result = run_test(test)

        results.append(result)

    with open(
        RESULTS_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            results,
            f,
            indent=2,
            ensure_ascii=False
        )

    print("\n\nExperiment completed.")

    print(f"Results saved to: {RESULTS_FILE}")


if __name__ == "__main__":
    main()